from apps.scraping.utils.proxy_tester import test_proxies_and_save
target_url= "https://smoothcomp.com/en/getBracketMatchData/10445731"
csv_output_dir="~/BjjDatabase/apps/scraping/scraper_smoothcomp/utils"
log_output_dir="~/BjjDatabase/logs"

test_proxies_and_save(
    target_url,
    csv_output_dir,
    log_output_dir,
    max_threads=20,
    test_mode=False,      # Only test 10 proxies
    verbose=False,        # Print progress
    include_socks=True   # Include SOCKS proxies
)