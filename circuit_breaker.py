from governance.logger import get_master_logger
logger = get_master_logger()

class GovernanceAgent:
    def __init__(self, template):
        self.template = template

    def check_status(self, metrics):
        if metrics.get('drawdown', 0) > self.template.get('max_drawdown', 0.05):
            logger.critical(f"CRITICAL_DRAWDOWN: {metrics['drawdown']}")
            return "RED", "CRITICAL_DRAWDOWN"
            
        margin_ratio = metrics.get('margin_ratio', 0.0)
        if margin_ratio > self.template.get('max_margin_ratio', 1.0):
            logger.critical(f"CRITICAL_MARGIN_SATURATION: Initial margin ratio {margin_ratio:.2f} exceeds limit.")
            return "RED", "CRITICAL_MARGIN_SATURATION"

        if metrics.get('trade_count_hourly', 0) > self.template.get('max_trades_per_hour', 50):
            logger.warning("LOGIC_DRIFT_THROTTLING")
            return "AMBER", "LOGIC_DRIFT_THROTTLING"
            
        return "GREEN", "OPERATIONAL"
