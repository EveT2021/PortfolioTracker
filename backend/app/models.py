from datetime import datetime

from . import db

# Keep models aligned with design.txt and db__schema.sql


class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(255), unique=True, nullable=False)
	password_hash = db.Column(db.String(128), nullable=False)
	name = db.Column(db.String(120))
	created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AssetType(db.Model):
	__tablename__ = 'asset_types'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False, unique=True)
	description = db.Column(db.Text)
	schema_hint = db.Column(db.JSON)


class Asset(db.Model):
	__tablename__ = 'assets'
	id = db.Column(db.Integer, primary_key=True)
	type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False)
	name = db.Column(db.String(255), nullable=False)
	symbol = db.Column(db.String(20))
	metadata_json = db.Column('metadata', db.JSON, default={})
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Portfolio(db.Model):
	__tablename__ = 'portfolios'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Holding(db.Model):
	__tablename__ = 'holdings'
	portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id', ondelete='CASCADE'), primary_key=True)
	asset_id = db.Column(db.Integer, db.ForeignKey('assets.id', ondelete='CASCADE'), primary_key=True)
	quantity = db.Column(db.Numeric(18, 8), nullable=False)
	cost_basis = db.Column(db.Numeric(14, 2), nullable=False)
	updated_at = db.Column(db.DateTime, default=datetime.utcnow)


class Transaction(db.Model):
	__tablename__ = 'transactions'
	id = db.Column(db.BigInteger, primary_key=True)
	portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id', ondelete='CASCADE'), nullable=False)
	asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
	type = db.Column(db.Enum('buy', 'sell', 'dividend', 'split', 'transfer_in', 'transfer_out', 'fee', name='transaction_type'), nullable=False)
	quantity = db.Column(db.Numeric(18, 8), nullable=False)
	price_per_unit = db.Column(db.Numeric(14, 6))
	total_amount = db.Column(db.Numeric(14, 2))
	fees = db.Column(db.Numeric(10, 2), default=0)
	executed_at = db.Column(db.DateTime, nullable=False)
	notes = db.Column(db.Text)
	created_at = db.Column(db.DateTime, default=datetime.utcnow)
