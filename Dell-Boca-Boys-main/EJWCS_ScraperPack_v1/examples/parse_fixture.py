from scraper.adapters.greenhouse import parse_greenhouse_job
from scraper.normalizers.location import normalize_location
from scraper.normalizers.compensation import normalize_compensation
from scraper.normalizers.seniority import infer_seniority

def run():
    with open("tests/golden/greenhouse_staff_accountant.html","r",encoding="utf-8") as f:
        html = f.read()
    url = "https://careers.acme.example/jobs/ACC-001"
    jp = parse_greenhouse_job(html, url)
    assert jp, "Parser failed to find JobPosting JSON-LD"
    jp.location_geo = normalize_location(jp.location_raw)
    jp.seniority_tag = infer_seniority(jp.title)
    lo, hi, cur = normalize_compensation("USD 80k - 110k")
    jp.comp_annual_min, jp.comp_annual_max, jp.currency = lo, hi, cur
    print(jp.model_dump_json(indent=2, ensure_ascii=False))

if __name__ == "__main__":
    run()
