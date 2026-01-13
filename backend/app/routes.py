from flask import Blueprint, jsonify, request
from . import db
from .models import User, Asset, Transaction, AssetType, Portfolio, Holding

api_bp = Blueprint('api', __name__)


@api_bp.route('/health')
def health():
	return jsonify({"status": "ok"})


@api_bp.route('/asset_types', methods=['GET', 'POST'])
def asset_types():
	if request.method == 'GET':
		types = AssetType.query.all()
		return jsonify([{"id": t.id, "name": t.name, "description": t.description} for t in types])

	data = request.get_json() or {}
	name = data.get('name')
	if not name:
		return jsonify({"error": "name required"}), 400

	at = AssetType(name=name, description=data.get('description'), schema_hint=data.get('schema_hint'))
	db.session.add(at)
	db.session.commit()
	return jsonify({"id": at.id, "name": at.name}), 201


@api_bp.route('/assets', methods=['GET', 'POST'])
def assets():
	if request.method == 'GET':
		assets = Asset.query.all()
		return jsonify([{"id": a.id, "symbol": a.symbol, "name": a.name} for a in assets])

	data = request.get_json() or {}
	symbol = data.get('symbol')
	name = data.get('name')
	type_id = data.get('type_id')
	if not name or not type_id:
		return jsonify({"error": "name and type_id required"}), 400

	a = Asset(symbol=symbol, name=name, type_id=type_id, metadata_json=data.get('metadata', {}))
	db.session.add(a)
	db.session.commit()
	return jsonify({"id": a.id, "symbol": a.symbol}), 201


@api_bp.route('/portfolios', methods=['GET', 'POST'])
def portfolios():
	if request.method == 'GET':
		ports = Portfolio.query.all()
		return jsonify([{"id": p.id, "user_id": p.user_id, "name": p.name} for p in ports])

	data = request.get_json() or {}
	user_id = data.get('user_id')
	name = data.get('name')
	if not user_id or not name:
		return jsonify({"error": "user_id and name required"}), 400

	p = Portfolio(user_id=user_id, name=name, description=data.get('description'))
	db.session.add(p)
	db.session.commit()
	return jsonify({"id": p.id, "name": p.name}), 201


@api_bp.route('/holdings', methods=['GET', 'POST'])
def holdings():
	if request.method == 'GET':
		portfolio_id = request.args.get('portfolio_id')
		if not portfolio_id:
			return jsonify({"error": "portfolio_id required"}), 400
		hs = Holding.query.filter_by(portfolio_id=portfolio_id).all()
		return jsonify([{"asset_id": h.asset_id, "quantity": str(h.quantity), "cost_basis": str(h.cost_basis)} for h in hs])

	data = request.get_json() or {}
	portfolio_id = data.get('portfolio_id')
	asset_id = data.get('asset_id')
	quantity = data.get('quantity')
	cost_basis = data.get('cost_basis')
	if not portfolio_id or not asset_id or quantity is None or cost_basis is None:
		return jsonify({"error": "portfolio_id, asset_id, quantity and cost_basis required"}), 400

	h = Holding(portfolio_id=portfolio_id, asset_id=asset_id, quantity=quantity, cost_basis=cost_basis)
	db.session.add(h)
	db.session.commit()
	return jsonify({"portfolio_id": h.portfolio_id, "asset_id": h.asset_id}), 201


@api_bp.route('/transactions', methods=['GET', 'POST'])
def transactions():
	if request.method == 'GET':
		txs = Transaction.query.order_by(Transaction.executed_at.desc()).limit(100).all()
		return jsonify([{"id": t.id, "asset_id": t.asset_id, "quantity": str(t.quantity), "price_per_unit": str(t.price_per_unit), "executed_at": t.executed_at.isoformat()} for t in txs])

	data = request.get_json() or {}
	asset_id = data.get('asset_id')
	portfolio_id = data.get('portfolio_id')
	quantity = data.get('quantity')
	ttype = data.get('type')
	if not asset_id or not portfolio_id or quantity is None or not ttype:
		return jsonify({"error": "asset_id, portfolio_id, quantity and type required"}), 400

	t = Transaction(asset_id=asset_id, portfolio_id=portfolio_id, quantity=quantity, type=ttype, price_per_unit=data.get('price_per_unit'), total_amount=data.get('total_amount'), executed_at=data.get('executed_at') or datetime.utcnow())
	db.session.add(t)
	db.session.commit()
	return jsonify({"id": t.id}), 201
