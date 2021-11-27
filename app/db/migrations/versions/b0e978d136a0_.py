"""Add more cities

Revision ID: b0e978d136a0
Revises: 375710df0a7b
Create Date: 2021-11-27 12:17:59.934590

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'b0e978d136a0'
down_revision = '375710df0a7b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

    op.execute('''
        INSERT INTO city
        VALUES
            ('Лондон', 'LHR'),
            ('Франкфурт', 'FRA'),
            ('Симферополь', 'SIP'),
            ('Осло', 'OSL'),
            ('Афины', 'ATH'),
            ('Дублин', 'DUB'),
            ('Милан', 'MXP'),
            ('Манчестер', 'MAN'),
            ('Брюссель', 'BRU'),
            ('Дюссельдорф', 'DUS'),
            ('Стокгольм', 'ARN'),
            ('Берлин', 'BER'),
            ('Женева', 'GVA'),
            ('Варшава', 'WAW'),
            ('Хельсинки', 'HEL'),
            ('Бухарест', 'OTP'),
            ('Марсель', 'MRS')
    ''')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###

    op.execute('''
        DELETE FROM city
        WHERE name IN (
            'Лондон',
            'Франкфурт',
            'Симферополь',
            'Осло',
            'Афины',
            'Дублин',
            'Милан',
            'Манчестер',
            'Брюссель',
            'Дюссельдорф',
            'Стокгольм',
            'Берлин',
            'Женева',
            'Варшава',
            'Хельсинки',
            'Бухарест',
            'Марсель'
        )
    ''')