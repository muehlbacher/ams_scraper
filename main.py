import sys
from scrape_class import AMS_JOBS

if __name__ == "__main__":
    print("start scraping...")
    url = "https://jobs.ams.at/public/emps/jobs?page=1&query=%C3%B6konom&JOB_OFFER_TYPE=SB_WKO&JOB_OFFER_TYPE=IJ&PERIOD=ALL&sortField=_SCORE"
    # url = "https://jobs.ams.at/public/emps/jobs?page=2&query=%C3%B6konom&location=Linz&JOB_OFFER_TYPE=SB_WKO&JOB_OFFER_TYPE=IJ&JOB_OFFER_TYPE=BA&PERIOD=ALL&sortField=_SCORE"
    arguments = []
    filename = "test.json"

    print("Script name:", sys.argv[0])
    # The rest of the items are the arguments
    if len(sys.argv) > 1:
        print("Arguments:")
        for arg in sys.argv[1:]:
            arguments.append(arg)
            print(arg)

        url = arguments[0]
        filename = arguments[1]
    else:
        print("No arguments provided")

    ams = AMS_JOBS(url, filename)

    ams.scrape()