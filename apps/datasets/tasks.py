from sodapy import Socrata


def scrape_datasets(dataset):
    dataportal = dataset.dataportal
    domain = dataportal.domain
    client = Socrata(domain, None)
    dataset.sourced_meta_data = client.get_metadata(dataset.identifier)
