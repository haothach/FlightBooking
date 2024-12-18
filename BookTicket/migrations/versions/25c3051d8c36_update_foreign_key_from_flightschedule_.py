"""Update foreign key from FlightSchedule to FlightRoute in IntermediateAirport

Revision ID: 25c3051d8c36
Revises: 
Create Date: 2024-11-29 20:08:34.482889

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '25c3051d8c36'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order')
    op.drop_table('flight_schedule')
    op.drop_table('ticket_class')
    op.drop_table('intermediate_airport')
    op.drop_table('seat')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index('username')

    op.drop_table('user')
    op.drop_table('flight_route')
    op.drop_table('bill')
    op.drop_table('airport')
    op.drop_table('province')
    op.drop_table('ticket')
    op.drop_table('order_detail')
    op.drop_table('flight')
    op.drop_table('airplane')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('airplane',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('airplane_type', mysql.ENUM('Bamboo_AirWays', 'Vietjet_Air', 'VietNam_Airline'), nullable=False),
    sa.Column('capacity', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('flight',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('flight_route_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('airplane_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['airplane_id'], ['airplane.id'], name='flight_ibfk_2'),
    sa.ForeignKeyConstraint(['flight_route_id'], ['flight_route.id'], name='flight_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('order_detail',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('quantity', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('unit_price', mysql.FLOAT(), nullable=True),
    sa.Column('total', mysql.FLOAT(), nullable=True),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.Column('ticket_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('order_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], name='order_detail_ibfk_2'),
    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], name='order_detail_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('ticket',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.Column('ticket_class_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('flight_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['flight_id'], ['flight.id'], name='ticket_ibfk_2'),
    sa.ForeignKeyConstraint(['ticket_class_id'], ['ticket_class.id'], name='ticket_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('province',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('airport',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('add', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('province_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['province_id'], ['province.id'], name='airport_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('bill',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('issueDate', mysql.DATETIME(), nullable=False),
    sa.Column('total', mysql.FLOAT(), nullable=False),
    sa.Column('is_Paid', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('note', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=True),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('flight_route',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('dep_airport_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('des_airport_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['dep_airport_id'], ['airport.id'], name='flight_route_ibfk_1'),
    sa.ForeignKeyConstraint(['des_airport_id'], ['airport.id'], name='flight_route_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('user',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('username', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('password', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=False),
    sa.Column('avatar', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=True),
    sa.Column('active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('user_role', mysql.ENUM('ADMIN', 'USER', 'STAFF'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index('username', ['username'], unique=True)

    op.create_table('seat',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('seat_class', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_available', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.Column('airplane_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('ticket_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['airplane_id'], ['airplane.id'], name='seat_ibfk_1'),
    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], name='seat_ibfk_2'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('intermediate_airport',
    sa.Column('airport_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('flight_schedule_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('stop_time', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('note', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=100), nullable=True),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['airport_id'], ['airport.id'], name='intermediate_airport_ibfk_1'),
    sa.ForeignKeyConstraint(['flight_schedule_id'], ['flight_schedule.id'], name='intermediate_airport_ibfk_2'),
    sa.PrimaryKeyConstraint('airport_id', 'flight_schedule_id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('ticket_class',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=50), nullable=False),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('flight_schedule',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('dep_date', mysql.DATETIME(), nullable=False),
    sa.Column('flight_time', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('first_class_seat_size', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('first_class_ticket_price', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('second_class_seat_size', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('second_class_ticket_price', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.Column('flight_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['flight_id'], ['flight.id'], name='flight_schedule_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('order',
    sa.Column('id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('order_day', mysql.DATETIME(), nullable=False),
    sa.Column('order_method', mysql.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('date_created', mysql.DATETIME(), nullable=True),
    sa.Column('bill_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['bill_id'], ['bill.id'], name='order_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_unicode_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    # ### end Alembic commands ###
