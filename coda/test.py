#!/usr/bin/env python
# This file is part of febelfin-coda.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
"""Test MT940
"""
import doctest
import os
import unittest
import sys
from datetime import date
from decimal import Decimal

from coda import CODA

here = os.path.dirname(__file__)
readme = os.path.normpath(os.path.join(here, '..', 'README'))


class TestCODA(unittest.TestCase):

    def setUp(self):
        self.coda = CODA(os.path.join(here, 'CODA.txt'))

    @property
    def statement(self):
        return self.coda.statements[0]

    @property
    def move(self):
        return self.statement.moves[0]

    def get_move(self, sequence, detail_sequence):
        return self.statement.find_move(sequence, detail_sequence)

    @property
    def information(self):
        return self.statement.informations['OL9456574JBBNEUBCRCL1'][0]

    def get_information(self, sequence, detail_sequence):
        for informations in self.statement.informations.values():
            for information in informations:
                if (information.sequence == sequence
                        and information.detail_sequence == detail_sequence):
                    return information

    def test_number_statements(self):
        self.assertEqual(len(self.coda.statements), 1)

    def test_statement_str(self):
        self.assertEqual(str(self.statement), '001')

    def test_statement_creation_date(self):
        self.assertEqual(self.statement.creation_date, date(2006, 12, 6))

    def test_statement_bank_id(self):
        self.assertEqual(self.statement.bank_id, 725)

    def test_statement_duplicate(self):
        self.assertEqual(self.statement.duplicate, False)

    def test_statement_file_reference(self):
        self.assertEqual(self.statement.file_reference, '00099449')

    def test_statement_address(self):
        self.assertEqual(self.statement.address, 'Testgebruiker21')

    def test_statement_bic(self):
        self.assertEqual(self.statement.bic, 'KREDBEBB')

    def test_statement_company_id(self):
        self.assertEqual(self.statement.company_id, '00630366277')

    def test_statement_version(self):
        self.assertEqual(self.statement.version, 2)

    def test_statement_old_sequence(self):
        self.assertEqual(self.statement.old_sequence, '001')

    def test_statement_new_sequence(self):
        self.assertEqual(self.statement.new_sequence, '001')

    def test_statement_account(self):
        self.assertEqual(self.statement.account, '435000000080')

    def test_statement_account_currency(self):
        self.assertEqual(self.statement.account_currency, 'EUR')

    def test_statement_account_country(self):
        self.assertEqual(self.statement.account_country, 'BE')

    def test_statement_old_balance(self):
        self.assertEqual(self.statement.old_balance, Decimal('0.000'))

    def test_statement_old_balance_date(self):
        self.assertEqual(self.statement.old_balance_date, date(2006, 12, 6))

    def test_statement_new_balance(self):
        self.assertEqual(self.statement.new_balance, Decimal('9405296.990'))

    def test_statement_new_balance_date(self):
        self.assertEqual(self.statement.new_balance_date, date(2006, 12, 7))

    def test_statement_account_holder_name(self):
        self.assertEqual(self.statement.account_holder_name, 'Testgebruiker21')

    def test_statement_account_description(self):
        self.assertEqual(
            self.statement.account_description, 'KBC-Bedrijfsrekening')

    def test_statement_coda_sequence(self):
        self.assertEqual(self.statement.coda_sequence, '001')

    def test_statement_number_records(self):
        self.assertEqual(self.statement.number_records, 260)

    def test_statement_total_debit(self):
        amount = sum(m.amount for m in self.statement.moves if m.amount < 0)
        self.assertEqual(self.statement.total_debit, -amount)

    def test_statement_total_credit(self):
        amount = sum(m.amount for m in self.statement.moves if m.amount > 0)
        self.assertEqual(self.statement.total_credit, amount)

    def test_statement_find(self):
        move = self.statement.find_move('0041', '0001')

        self.assertEqual(move.sequence, '0041')
        self.assertEqual(move.detail_sequence, '0001')

    def test_moves(self):
        self.assertEqual(len(list(self.statement.moves)), 59)

    def test_move_str(self):
        self.assertEqual(str(self.move), '00010000')

    def test_move_sequence(self):
        self.assertEqual(self.move.sequence, '0001')

    def test_move_detail_sequence(self):
        self.assertEqual(self.move.detail_sequence, '0000')

    def test_move_bank_reference(self):
        self.assertEqual(self.move.bank_reference, 'EPIB00048 AWIUBTKAPUO')

    def test_move_amount(self):
        self.assertEqual(self.move.amount, Decimal('-2578.25'))

    def test_move_value_date(self):
        self.assertEqual(self.move.value_date, date(2006, 12, 6))

    def test_move_transaction_code(self):
        self.assertEqual(self.move.transaction_code, '00799000')

    def test_move_transaction_type(self):
        self.assertEqual(self.move.transaction_type, '0')

    def test_move_transaction_family(self):
        self.assertEqual(self.move.transaction_family, '07')

    def test_move_transaction_transaction(self):
        self.assertEqual(self.move.transaction_transaction, '99')

    def test_move_transaction_category(self):
        self.assertEqual(self.move.transaction_category, '000')

    def test_move_communication_type(self):
        self.assertEqual(self.move.communication_type, None)

    def test_move_communication(self):
        self.assertEqual(
            self.move.communication,
            "BORDEREAU DE DECOMPTE AVANCES    015 NUMERO D'OPERATION 495953")

    def test_move_communication_101(self):
        move = self.get_move('0053', '0000')

        self.assertEqual(move.communication_type, '101')
        self.assertEqual(move.communication, '269021157996')

    def test_move_communication_105(self):
        move = self.get_move('0003', '0002')

        self.assertEqual(move.communication_type, '105')
        self.assertEqual(move.communication, '')

    def test_move_communication_106(self):
        move = self.get_move('0004', '0003')

        self.assertEqual(move.communication_type, '106')
        self.assertEqual(move.communication, None)

    def test_move_communication_111(self):
        move = self.get_move('0009', '0000')

        self.assertEqual(move.communication_type, '111')
        self.assertEqual(move.communication, None)

    def test_move_communication_113(self):
        move = self.get_move('0012', '0000')

        self.assertEqual(move.communication_type, '113')
        self.assertEqual(move.communication, None)

    def test_move_communication_114(self):
        move = self.get_move('0043', '0001')

        self.assertEqual(move.communication_type, '114')
        self.assertEqual(move.communication, None)

    def test_move_communication_115(self):
        move = self.get_move('0049', '0000')

        self.assertEqual(move.communication_type, '115')
        self.assertEqual(move.communication, None)

    def test_move_entry_date(self):
        self.assertEqual(self.move.entry_date, date(2006, 12, 6))

    def test_move_statement_number(self):
        self.assertEqual(self.move.statement_number, '001')

    def test_move_customer_reference(self):
        move = self.get_move('0004', '0000')

        self.assertEqual(move.customer_reference, 'NB2206092900135')

    def test_move_counterparty_bic(self):
        move = self.get_move('0006', '0000')

        self.assertEqual(move.counterparty_bic, 'CREGBEBB')

    def test_move_r_transaction(self):
        move = self.get_move('0003', '0000')

        self.assertEqual(move.r_transaction, '4')

    def test_move_r_reason(self):
        move = self.get_move('0003', '0000')

        self.assertEqual(move.r_reason, '3246')

    def test_move_category_purpose(self):
        move = self.get_move('0003', '0000')

        self.assertEqual(move.category_purpose, '306A')

    def test_move_purpose(self):
        move = self.get_move('0003', '0000')

        self.assertEqual(move.purpose, '1648')

    def test_move_counterparty_account(self):
        move = self.get_move('0003', '0000')

        self.assertEqual(move.counterparty_account, 'LU037050522702273100')

    def test_move_counterparty_name(self):
        move = self.get_move('0003', '0000')

        self.assertEqual(move.counterparty_name, ' Olgerdin Egill Skallagrims')

    def test_informations(self):
        self.assertEqual(len(self.statement.informations), 22)

    def test_information_str(self):
        self.assertEqual(str(self.information), '00030001')

    def test_information_sequence(self):
        self.assertEqual(self.information.sequence, '0003')

    def test_information_detail_sequence(self):
        self.assertEqual(self.information.detail_sequence, '0001')

    def test_information_bank_reference(self):
        self.assertEqual(
            self.information.bank_reference, 'OL9456574JBBNEUBCRCL1')

    def test_information_transaction_code(self):
        self.assertEqual(self.information.transaction_code, '34150000')

    def test_information_communitcation_type(self):
        self.assertEqual(self.information.communication_type, '001')

    def test_information_communitcation_name(self):
        self.assertEqual(self.information.name, 'Olgerdin Egill Skallagrims')

    def test_information_communitcation_street(self):
        self.assertEqual(self.information.street, 'Grjothalsi 7')

    def test_information_communitcation_locality(self):
        self.assertEqual(self.information.locality, '11110 Reykjavik')

    def test_information_communitcation_code_id(self):
        self.assertEqual(self.information.code_id, '')

    def test_information_counterparty_banker(self):
        information = self.get_information('0058', '0002')

        self.assertEqual(information.counterparty_banker, 'SOCIETE GENERALE')

    def test_information_coin_number(self):
        information = self.get_information('0049', '0001')

        self.assertEqual(information.coin_number, 1)

    def test_information_coin(self):
        information = self.get_information('0049', '0001')

        self.assertEqual(information.coin, Decimal('10'))

    def test_information_total_amount(self):
        information = self.get_information('0049', '0001')

        self.assertEqual(information.total_amount, Decimal('10'))

    def test_sum_moves(self):
        amount = sum(m.amount for m in self.statement.moves)
        self.assertEqual(
            amount, self.statement.new_balance - self.statement.old_balance)

    def test_sum_details(self):
        move = self.get_move('0002', '0000')
        amount = sum(m.amount for m in move.moves)

        self.assertEqual(amount, move.amount)


def test_suite():
    suite = additional_tests()
    loader = unittest.TestLoader()
    suite.addTests(loader.loadTestsFromTestCase(TestCODA))
    return suite


def additional_tests():
    suite = unittest.TestSuite()
    if os.path.isfile(readme):
        suite.addTest(doctest.DocFileSuite(readme, module_relative=False))
    return suite


def main():
    suite = test_suite()
    runner = unittest.TextTestRunner()
    return runner.run(suite)


if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))
    sys.exit(not main().wasSuccessful())
