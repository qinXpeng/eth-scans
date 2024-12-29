# ETH Scans

## 项目简介
ETH Scans 是一个用于扫描和分析以太坊区块链数据的工具。它可以帮助用户获取区块链上的交易信息、账户余额以及其他相关数据。

## 功能特点
- 获取以太坊区块链上的最新区块和交易信息
- 查询指定账户的余额和交易记录
- 支持多种查询和过滤条件
- 提供详细的交易和区块分析报告

## 安装和运行
### 前提条件
- Python 3.7+
- pip

### 安装步骤
1. 克隆项目仓库：
    ```bash
    git clone https://github.com/yourusername/eth-scans.git
    cd eth-scans
    ```

2. 安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

### 运行项目
```bash
python eth_scan.py
```

## 依赖项
- web3: ^5.24.0

## 使用示例
以下是一个简单的使用示例，展示如何运行扫描器并获取区块链数据：
```python
from eth_scan import ScanEth

RPC_URL_LIST = [
    "https://eth.drpc.org",
    "https://rpc.mevblocker.io/fast",
    "https://eth.rpc.blxrbdn.com",
    "https://eth.blockrazor.xyz",
    "https://1rpc.io/eth",
    "https://eth-mainnet.nodereal.io/v1/1659dfb40aa24bbb8153a677b98064d7",
    "https://mainnet.gateway.tenderly.co",
    "https://eth1.lava.build"
]

scanner = ScanEth(RPC_URL_LIST)
scanner.run()
```

## 贡献指南
欢迎贡献者提交问题、功能请求和代码贡献。请确保在提交之前阅读并遵循我们的贡献指南。

## 许可证
本项目采用 MIT 许可证。详情请参阅 [LICENSE](./LICENSE) 文件。
