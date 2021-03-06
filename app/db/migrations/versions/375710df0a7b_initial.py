"""initial

Revision ID: 375710df0a7b
Revises: 
Create Date: 2021-11-23 20:02:11.705853

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '375710df0a7b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('city',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('airport', sa.String(length=3), nullable=False),
    sa.PrimaryKeyConstraint('name', 'airport')
    )
    op.create_table('flight',
    sa.Column('destination', sa.String(length=50), nullable=False),
    sa.Column('parsing_date', sa.Date(), nullable=False),
    sa.Column('departure_date', sa.Date(), nullable=False),
    sa.Column('days_until', sa.Integer(), nullable=False),
    sa.Column('airlines', sa.String(length=50), nullable=False),
    sa.Column('departure_time', sa.Time(), nullable=False),
    sa.Column('arrival_time', sa.Time(), nullable=False),
    sa.Column('duration_m', sa.Integer(), nullable=False),
    sa.Column('departure_airport', sa.String(length=3), nullable=False),
    sa.Column('arrival_airport', sa.String(length=3), nullable=False),
    sa.Column('min_price', sa.Integer(), nullable=False),
    sa.Column('stops_count', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['arrival_airport'], ['city.airport'], ),
    sa.ForeignKeyConstraint(['destination'], ['city.name'], ),
    sa.PrimaryKeyConstraint('destination', 'parsing_date', 'departure_date', 'days_until', 'airlines', 'departure_time', 'arrival_time', 'duration_m', 'departure_airport', 'arrival_airport', 'min_price', 'stops_count')
    )
    # ### end Alembic commands ###

    op.execute('''
        INSERT INTO city
        VALUES
            ('Будапешт', 'BUD')
        ,   ('Лиссабон', 'LIS')
        ,   ('Амстердам', 'AMS')
        ,   ('Барселона', 'BCN')
        ,   ('Мюнхен', 'MUC')
        ,   ('Рим', 'FCO')
        ,   ('Вена', 'VIE')
        ,   ('Краков', 'KRK')
        ,   ('Прага', 'PRG')
        ,   ('Копенгаген', 'CPH')
        ,   ('Таллин', 'TLL')
        ,   ('Ницца', 'NCE')
        ,   ('Эдинбург', 'EDI')
        ,   ('Цюрих', 'ZRH')
        ,   ('Мадрид', 'MAD')
        ,   ('Стамбул', 'IST')
        ,   ('Флоренция', 'FLR')
        ,   ('Любляна', 'LJU')
        ,   ('Париж', 'CDG')
    ''')


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('flight')
    op.drop_table('city')
    # ### end Alembic commands ###
