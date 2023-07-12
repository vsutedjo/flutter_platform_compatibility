import yaml
import requests
from bs4 import BeautifulSoup
import csv

# The filepath to the pubspec.yaml file of your project.
pubspec_filepath = "my_project/pubspec.yaml"
# The filepath to the csv file to which the results should be written.
csv_filepath = "platform_compatibility.csv"

# Comment out the platforms you don't require.
searched_platforms = ["Android", "iOS", "Windows", "Linux", "macOS", "Web"]


def flutter_compatibility_checker(input_filepath, output_filepath):
    with open(input_filepath, "r") as stream:
        with open(output_filepath, 'w', newline='') as csvfile:
            try:
                writer = csv.writer(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

                # Write the header first row.
                header_row = ["package"] + ["version/fork"]
                for platform in searched_platforms:
                    header_row += [platform]
                header_row += ["url"]
                writer.writerow(header_row)

                # Define the type of packages we are considering.
                data = yaml.safe_load(stream)
                packages = data.get('dependency_overrides')
                packages.update(data.get('dependencies'))

                package_names = packages.keys()

                for package in package_names:
                    package_row = [package]

                    # Check if we are using a forked version of this package.
                    if type(packages[package]) is dict and "git" in packages[package].keys():
                        version = packages[package]["git"]["url"]
                    else:
                        version = packages[package]
                    package_row += [version]

                    # Scrape the url of the package for windows compatibility tag.
                    url = "https://pub.dev/packages/" + package
                    r = requests.get(url)
                    soup = BeautifulSoup(r.text, 'html.parser')

                    for platform in searched_platforms:
                        # The html expression we are searching for.
                        platform_tag = platform
                        if platform == "Web":
                            platform_tag= platform.lower()
                        filter_expr = '<a class="tag-badge-sub" href="/packages?q=platform%3A'+platform.lower()+'" rel="nofollow" ' \
                                      'title="Packages compatible with ' + platform + ' platform">'+ platform_tag +'</a>'
                        platform_compatible = len(list(filter(lambda entry: str(
                            entry.parent) == filter_expr, soup.body.findAll(text=platform_tag)))) > 0
                        package_row += [platform_compatible]

                    # Add the url of the package to the table.
                    package_row += [url]

                    # Write results into the csv file.
                    writer.writerow(package_row)
                print("DONE")

            except yaml.YAMLError as exc:
                print(exc)


if __name__ == "__main__":
    pubspec_file = flutter_compatibility_checker(pubspec_filepath, csv_filepath)
