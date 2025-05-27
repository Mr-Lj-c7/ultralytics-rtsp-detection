import json
from logger import logger

def load_config(config_path):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    
    except FileNotFoundError as e:
        logger.error(f"未找到配置文件: {config_path}")
        raise FileNotFoundError(f"未找到配置文件: {config_path}") from e
    except json.JSONDecodeError as e:
        logger.error(f"配置文件内容无效,JSON 解析失败: {e}")
        raise ValueError(f"配置文件内容无效,JSON 解析失败: {e}") from e
    finally:
        f.close()
        logger.info("配置文件加载完成")
