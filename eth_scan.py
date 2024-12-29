from web3 import Web3
import time
import logging
from typing import Set, Dict
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('eth_scan.log'),
        logging.StreamHandler()
    ]
)

class ScanEth:
    def __init__(self, rpc_list):
        self.rpc_list = rpc_list
        self.wb_list = []
        for rpc in self.rpc_list:
            h = Web3(Web3.HTTPProvider(rpc))
            self.wb_list.append(h)
            if not h.is_connected():
                logging.error("Failed to connect to the Ethereum node")
                exit(1)
        
        # 初始化数据结构
        self.address_map: Dict[str, bool] = {}
        self.flush_address_list: Set[str] = set()
        self.batch_size = 1000  # 每批处理的区块数
        self.retry_count = 3    # 重试次数
        self.retry_delay = 3    # 重试延迟（秒）
        self.wb_index = 0
        self.wb_len = len(self.wb_list)
        # 加载初始数据
        self.block_num = self._load_block_num()
        self._load_addresses()
        logging.info(f"Initialized with block number: {self.block_num}")
        logging.info(f"Loaded {len(self.address_map)} addresses")

    def _load_block_num(self) -> int:
        """从文件加载起始区块号，如果文件不存在则获取最新区块号"""
        try:
            if os.path.exists('block_num.txt'):
                with open('block_num.txt', 'r') as f:
                    return int(f.read().strip())
            return self._get_wb().eth.block_number
        except Exception as e:
            logging.error(f"Error loading block number: {e}")
            return self._get_wb().eth.block_number
    def _get_wb(self) -> Web3:
        self.wb_index += 1
        return self.wb_list[self.wb_index%self.wb_len]
    def _load_addresses(self) -> None:
        """从文件加载已扫描的地址"""
        try:
            if os.path.exists('eth_address.txt'):
                with open('eth_address.txt', 'r') as f:
                    for line in f:
                        addr = line.strip().lower()
                        if addr:
                            self.address_map[addr] = True
        except Exception as e:
            logging.error(f"Error loading addresses: {e}")

    def _save_progress(self, block_num: int) -> None:
        """保存进度（区块号和新地址）"""
        try:
            # 保存区块号
            with open('block_num.txt', 'w') as f:
                f.write(str(block_num))
            
            # 保存新地址
            if self.flush_address_list:
                with open('eth_address.txt', 'a') as f:
                    for addr in self.flush_address_list:
                        f.write(f"{addr}\n")
                self.flush_address_list.clear()
            logging.info(f"Progress saved at block {block_num}")
        except Exception as e:
            logging.error(f"Error saving progress: {e}")

    def _process_address(self, address: str) -> None:
        """处理单个地址"""
        if address and isinstance(address, str):
            address = address.lower()
            if address not in self.address_map:
                try:
                    # balance = self._get_wb().eth.get_balance(address)
                    # if balance > 0:
                    self.address_map[address] = True
                    self.flush_address_list.add(address)
                except Exception as e:
                    logging.error(f"Error checking balance for address {address}: {e}")

    def scan_block(self, block_number: int) -> None:
        """扫描单个区块"""
        for attempt in range(self.retry_count):
            try:
                block = self._get_wb().eth.get_block(block_number, full_transactions=True)
                for tx in block.transactions:
                    self._process_address(tx['from'])
                    self._process_address(tx['to'])
                return
            except Exception as e:
                if attempt < self.retry_count - 1:
                    logging.warning(f"Attempt {attempt + 1} failed for block {block_number}: {e}")
                    time.sleep(self.retry_delay)
                else:
                    logging.error(f"Failed to scan block {block_number} after {self.retry_count} attempts: {e}")
                    raise

    def run(self):
        blocks_processed = 0
        start_time = time.time()
        
        try:
            for block_num in range(self.block_num, 1, -1):
                try:
                    self.scan_block(block_num)
                    blocks_processed += 1
                    # 每处理batch_size个区块保存一次进度
                    if blocks_processed % self.batch_size == 0:
                        self._save_progress(block_num)
                        
                        # 计算和显示处理速度
                        elapsed_time = time.time() - start_time
                        blocks_per_second = blocks_processed / elapsed_time
                        logging.info(f"Processing speed: {blocks_per_second:.2f} blocks/second")
                        logging.info(f"Total addresses found: {len(self.address_map)}")

                except Exception as e:
                    logging.error(f"Error processing block {block_num}: {e}")
                    time.sleep(self.retry_delay)  # 出错时短暂暂停
                    
        except KeyboardInterrupt:
            logging.info("Scanning interrupted by user")
        finally:
            # 保存最终进度
            self._save_progress(block_num)
            logging.info("Scan completed")

if __name__ == "__main__":
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

