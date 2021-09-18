# This file is part of febelfin-coda.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
"""a parser for CODA files
"""
import io
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

__version__ = '0.2.0'
__all__ = ['CODA', 'Statement', 'Move', 'Information', 'FreeCommunication']


class CODA(object):

    def __init__(self, name, encoding='windows-1252'):
        self.statements = []

        if isinstance(name, (bytes, str)):
            with io.open(name, encoding=encoding, mode='r') as f:
                self._parse(f)
        else:
            self._parse(name)

    def _parse(self, f):
        statement = None
        total_credit, total_debit = 0, 0
        move = None
        information = None
        i = 0
        for record in f:
            type_ = record[0]
            if type_ == '0':
                statement = Statement()
                self.statements.append(statement)
                self._parse_statement(record, statement, HEADER)

                if statement.version != 2:
                    raise ValueError(
                        "Unsupported version %d" % statement.version)
            elif type_ == '1':
                self._parse_statement(record, statement, OLD_BALANCE)
            elif type_ == '2':
                article = record[1]
                if article == '1':
                    move = Move()
                self._parse_move(record, article, move)
                if article == '1':
                    transaction_type = move.transaction_type
                    if transaction_type in {'0', '1', '2', '3'}:
                        statement.moves.append(move)

                        if move.amount > 0:
                            total_credit += move.amount
                        else:
                            total_debit -= move.amount
                    elif transaction_type in {'5', '6', '7', '8'}:
                        parent = statement.moves[-1]
                        assert parent.sequence == move.sequence
                        parent.moves.append(move)
                    elif transaction_type == '9':
                        parent = statement.moves[-1].moves[-1]
                        assert parent.sequence == move.sequence
                        parent.append(move)
                    else:
                        raise ValueError('Unknown type: %s' % transaction_type)
            elif type_ == '3':
                article = record[1]
                if article == '1':
                    information = Information()
                self._parse_information(record, article, information)
                if article == '1':
                    key = information.bank_reference
                    statement.informations[key].append(information)
            elif type_ == '4':
                free_communication = FreeCommunication()
                self._parse_free_communication(record, free_communication)
                self.free_communications.append(free_communication)
            elif type_ == '8':
                self._parse_statement(record, statement, NEW_BALANCE)
            elif type_ == '9':
                self._parse_statement(record, statement, TRAILER)

                if (statement.new_balance - statement.old_balance
                        != statement.total_credit - statement.total_debit):
                    raise ValueError("Wrong balance")
                if statement.total_credit != total_credit:
                    raise ValueError("Wrong total credit")
                if statement.total_debit != total_debit:
                    raise ValueError("Wrong total debit")
                if statement.number_records != i - 1:
                    raise ValueError("Wrong number of records")
                statement = None
                total_credit, total_debit = 0, 0
                i = 0
            i += 1

    def _parse_statement(self, record, statement, desc):
        for name, (slice_, parser) in desc.items():
            value = parser(record[slice_])
            if getattr(statement, name) is not None:
                assert getattr(statement, name) == value, (name, value,
                    getattr(statement, name), statement)
            setattr(statement, name, value)

    def _parse_move(self, record, article, move):
        for name, (slice_, parser) in MOVE_COMMON.items():
            value = parser(record[slice_])
            if getattr(move, name) is not None:
                assert getattr(move, name) == value
            else:
                setattr(move, name, value)
        for name, (slice_, parser) in MOVE[article].items():
            value = parser(record[slice_])
            if getattr(move, name):
                value = getattr(move, name) + value
            setattr(move, name, value)

    def _parse_information(self, record, article, information):
        for name, (slice_, parser) in INFORMATION_COMMON.items():
            value = parser(record[slice_])
            if getattr(information, name) is not None:
                assert getattr(information, name) == value
            else:
                setattr(information, name, value)
        for name, (slice_, parser) in INFORMATION[article].items():
            value = parser(record[slice_])
            if getattr(information, name):
                value = getattr(information, name) + value
            setattr(information, name, value)

    def _parse_free_communication(self, record, free_communication):
        for name, (slice_, parser) in FREE_COMMUNICATION.items():
            value = parser(record[slice_])
            setattr(free_communication, name, value)


def _date(value):
    return datetime.strptime(value, '%d%m%y').date()


def _string(value):
    return value.rstrip()


def _amount(value):
    sign = value[0:1]
    amount = Decimal(value[1:])
    if sign == '1':
        amount *= -1
    return amount / 1000


HEADER = {
    'creation_date': (slice(5, 11), _date),
    'bank_id': (slice(11, 14), int),
    'duplicate': (slice(16, 17), lambda c: c == 'D'),
    'file_reference': (slice(24, 34), _string),
    'address': (slice(34, 60), _string),
    'bic': (slice(60, 71), _string),
    'company_id': (slice(71, 82), str),
    'reference': (slice(88, 104), _string),
    'related_reference': (slice(105, 120), _string),
    'version': (slice(127, 128), int),
    }
TRAILER = {
    'number_records': (slice(16, 22), int),
    'total_debit': (slice(22, 37), _amount),
    'total_credit': (slice(37, 52), _amount),
    }
OLD_BALANCE = {
    '_account_structure': (slice(1, 2), str),
    'old_sequence': (slice(2, 5), str),
    '_account_currency': (slice(5, 42), str),
    'old_balance': (slice(43, 58), _amount),
    'old_balance_date': (slice(58, 64), _date),
    'account_holder_name': (slice(64, 90), _string),
    'account_description': (slice(90, 125), _string),
    'coda_sequence': (slice(125, 128), str),
    }
NEW_BALANCE = {
    'new_sequence': (slice(1, 4), str),
    '_account_currency': (slice(4, 41), str),
    'new_balance': (slice(41, 57), _amount),
    'new_balance_date': (slice(57, 63), _date),
    }


class _SlotsNone(object):
    def __init__(self, *args, **kwargs):
        super(_SlotsNone, self).__init__(*args, **kwargs)
        for name in self.__slots__:
            setattr(self, name, None)


class _Moves(object):
    __slots__ = ('moves',)

    def __init__(self, *args, **kwargs):
        super(_Moves, self).__init__(*args, **kwargs)
        self.moves = []

    def find_move(self, sequence, detail_sequence='0000'):
        for move in self.moves:
            if move.sequence == sequence:
                if move.detail_sequence == detail_sequence:
                    return move
                found = move.find_move(sequence, detail_sequence)
                if found:
                    return found

    @property
    def all_moves(self):
        for move in self.moves:
            yield move
            for move in move.all_moves:
                yield move


class Statement(_SlotsNone, _Moves):
    __slots__ = (list(HEADER.keys()) + list(TRAILER.keys())
        + list(OLD_BALANCE.keys()) + list(NEW_BALANCE.keys())
        + ['informations', 'free_communications'])

    def __init__(self, *args, **kwargs):
        super(Statement, self).__init__(*args, **kwargs)
        self.informations = defaultdict(list)
        self.free_communications = []

    def __str__(self):
        if self.old_sequence != self.new_sequence:
            return ' - '.join([self.old_sequence, self.new_sequence])
        else:
            return self.old_sequence

    @property
    def account(self):
        return _string(self._account_currency[{
            '0': slice(0, 12),
            '1': slice(0, 34),
            '2': slice(0, 31),
            '3': slice(0, 34),
            }[self._account_structure]])

    @property
    def account_currency(self):
        return self._account_currency[{
                '0': slice(13, 16),
                '1': slice(34, 37),
                '2': slice(34, 37),
                '3': slice(34, 37),
                }[self._account_structure]]

    @property
    def account_country(self):
        if self._account_structure == '0':
            return self._account_currency[17:19]


class _TransactionMixin(object):

    @property
    def transaction_type(self):
        return self.transaction_code[0]

    @property
    def transaction_family(self):
        return self.transaction_code[1:3]

    @property
    def transaction_transaction(self):
        return self.transaction_code[3:5]

    @property
    def transaction_category(self):
        return self.transaction_code[5:8]


MOVE_COMMON = {
    'sequence': (slice(2, 6), str),
    'detail_sequence': (slice(6, 10), str),
    }
MOVE = {
    '1': {
        'bank_reference': (slice(10, 31), str),
        'amount': (slice(31, 47), _amount),
        'value_date': (slice(47, 53), _date),
        'transaction_code': (slice(53, 61), str),
        '_communication': (slice(61, 115), str),
        'entry_date': (slice(115, 121), _date),
        'statement_number': (slice(121, 124), str),
        },
    '2': {
        '_communication': (slice(10, 63), str),
        'customer_reference': (slice(63, 98), _string),
        'counterparty_bic': (slice(98, 109), _string),
        'r_transaction': (slice(112, 113), _string),
        'r_reason': (slice(113, 117), _string),
        'category_purpose': (slice(117, 121), _string),
        'purpose': (slice(121, 125), _string),
        },
    '3': {
        'counterparty_account': (slice(10, 47), _string),
        'counterparty_name': (slice(47, 82), _string),
        '_communication': (slice(82, 125), str),
        },
    }


class Move(_SlotsNone, _Moves, _TransactionMixin):
    __slots__ = sum(
        (list(m.keys()) for m in MOVE.values()), list(MOVE_COMMON.keys()))

    def __str__(self):
        return self.sequence + self.detail_sequence

    @property
    def communication(self):
        type_ = self.communication_type
        if type_ is None:
            return _string(self._communication[1:])
        elif type_ == '100':
            # TODO ISO-11649
            return self._communication[4:]
        elif type_ in {'101', '102', '103'}:
            return _string(self._communication[4:16])
        elif type_ == '105':
            return _string(self._communication[49:61])
        elif type_ in {'106', '108', '111', '113', '114', '115',
                '121', '122', '123', '124', '125', '126'}:
            return
        elif type_ == '127':
            return self._communication[83:145]
        else:
            return self._communication[2:]
    # TODO add parser communication

    @property
    def communication_type(self):
        type_ = self._communication[0]
        if type_ == '1':
            return self._communication[1:4]


INFORMATION_COMMON = {
    'sequence': (slice(2, 6), str),
    'detail_sequence': (slice(6, 10), str),
    }
INFORMATION = {
    '1': {
        'bank_reference': (slice(10, 31), str),
        'transaction_code': (slice(31, 39), str),
        '_communication': (slice(39, 113), str),
        },
    '2': {
        '_communication': (slice(10, 115), str),
        },
    '3': {
        '_communication': (slice(10, 100), str),
        },
    }


class Information(_SlotsNone, _TransactionMixin):
    __slots__ = sum(
        (list(m.keys()) for m in INFORMATION.values()),
        list(INFORMATION_COMMON.keys()))

    def __str__(self):
        return self.sequence + self.detail_sequence

    @property
    def communication_type(self):
        type_ = self._communication[0]
        if type_ == '1':
            return self._communication[1:4]

    @property
    def name(self):
        if self.communication_type in {'001', '008', '009'}:
            return _string(self._communication[4:74])
        else:
            raise AttributeError

    @property
    def street(self):
        if self.communication_type == '001':
            return _string(self._communication[74:109])
        else:
            raise AttributeError

    @property
    def locality(self):
        if self.communication_type == '001':
            return _string(self._communication[109:144])
        else:
            raise AttributeError

    @property
    def code_id(self):
        if self.communication_type == '001':
            return _string(self._communication[144:179])
        elif self.communication_type in {'008', '009'}:
            return _string(self._communication[74:109])
        else:
            raise AttributeError

    @property
    def communication(self):
        if self.communication_type == '002':
            return self._communication[4:]
        else:
            raise AttributeError

    @property
    def counterparty_banker(self):
        if self.communication_type == '004':
            return _string(self._communication[4:])
        else:
            raise AttributeError

    @property
    def correspondent_data(self):
        if self.communication_type == '005':
            return self._communication[4:]
        else:
            raise AttributeError

    @property
    def description(self):
        if self.communication_type == '006':
            return self._communication[4:34]
        else:
            raise AttributeError

    @property
    def currency(self):
        if self.communication_type == '006':
            return self._communication[34:37]
        else:
            raise AttributeError

    @property
    def amount(self):
        if self.communication_type == '006':
            return _amount(
                self._communication[53] + self._communication[37:52])
        else:
            raise AttributeError

    @property
    def category(self):
        if self.communication_type == '006':
            return self._communication[53:56]
        else:
            raise AttributeError

    @property
    def coin_number(self):
        if self.communication_type == '007':
            return int(self._communication[4:11])
        else:
            raise AttributeError

    @property
    def coin(self):
        if self.communication_type == '007':
            return Decimal(self._communication[11:17]) / 1000
        else:
            raise AttributeError

    @property
    def total_amount(self):
        if self.communication_type == '007':
            return Decimal(self._communication[17:32]) / 1000
        else:
            raise AttributeError

    # TODO communication type: 010 and 011


FREE_COMMUNICATION = {
    'sequence': (slice(2, 6), str),
    'detail_sequence': (slice(6, 10), str),
    'text': (slice(32, 112), _string),
    }


class FreeCommunication(_SlotsNone):
    __slots__ = list(FREE_COMMUNICATION.keys())
