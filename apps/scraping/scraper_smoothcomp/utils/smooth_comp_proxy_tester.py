import os

from apps.scraping.utils.proxy_tester import test_proxies_and_save

def test_smooth_comp_proxies(
    max_threads=20,
    test_mode=False,
    verbose=False,
    include_socks=True
):
    target_url = "https://smoothcomp.com/en/getBracketMatchData/10445731"

    # Expand `~` to absolute paths
    csv_output_dir = os.path.expanduser("~/BjjDatabase/apps/scraping/scraper_smoothcomp/utils")
    log_output_dir = os.path.expanduser("~/BjjDatabase/logs")

    test_proxies_and_save(
        target_url=target_url,
        csv_output_dir=csv_output_dir,
        log_output_dir=log_output_dir,
        max_threads=max_threads,
        test_mode=test_mode,
        verbose=verbose,
        include_socks=include_socks
    )

if __name__ == "__main__":
    test_smooth_comp_proxies(test_mode=True, verbose=True)
