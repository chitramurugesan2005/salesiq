from flask import Blueprint, jsonify
from ai_ml.forecast import run_forecast
from ai_ml.segment import run_segmentation

ai_bp = Blueprint('ai', __name__)


@ai_bp.route('/forecast', methods=['GET'])
def forecast():
    try:
        result, error = run_forecast()
        if error:
            return jsonify({"error": error}), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ai_bp.route('/segment', methods=['GET'])
def segment():
    try:
        result, error = run_segmentation()
        if error:
            return jsonify({"error": error}), 400
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
