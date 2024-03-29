febelfin-coda
=============

febelfin-coda is a parser for `CODA files`_.

.. _CODA files: http://downloads.tryton.org/standards/coda-2.6.pdf

Nutshell
--------

Import::

    >>> import os
    >>> from coda import CODA

Instantiate::

    >>> coda = CODA('coda/CODA.txt')

The statements::

    >>> len(coda.statements)
    1
    >>> statement, = coda.statements
    >>> statement.account
    '435000000080'
    >>> statement.account_currency
    'EUR'
    >>> statement.old_balance
    Decimal('0')
    >>> statement.old_balance_date
    datetime.date(2006, 12, 6)
    >>> statement.new_balance
    Decimal('9405296.99')
    >>> statement.new_balance_date
    datetime.date(2006, 12, 7)

The transactions::

    >>> len(statement.moves)
    59
    >>> move = statement.moves[0]
    >>> move.value_date
    datetime.date(2006, 12, 6)
    >>> move.entry_date
    datetime.date(2006, 12, 6)
    >>> move.amount
    Decimal('-2578.25')
    >>> move.bank_reference
    'EPIB00048 AWIUBTKAPUO'
    >>> move.transaction_code
    '00799000'
    >>> move.communication
    "BORDEREAU DE DECOMPTE AVANCES    015 NUMERO D'OPERATION 495953"

To report issues please visit the `coda bugtracker`_.

.. _coda bugtracker: https://bugs.tryton.org/coda
