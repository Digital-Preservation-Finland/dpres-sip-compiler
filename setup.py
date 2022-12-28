"""Install SIP Compiler."""
from setuptools import setup, find_packages


def main():
    """Install SIP Compiler."""
    setup(
        name='dpres_sip_compiler',
        packages=find_packages(exclude=["tests", "tests.*"]),
        package_dir={
            "dpres_sip_compiler": "dpres_sip_compiler"
        },
        include_package_data=True,
        install_requires=[
            "click",
            "xml_helpers@git+https://gitlab.ci.csc.fi/dpres/"
            "xml-helpers.git@develop#egg=xml_helpers",
            "premis@git+https://gitlab.ci.csc.fi/dpres/"
            "premis.git@develop#egg=premis",
            "file_scraper@git+https://gitlab.ci.csc.fi/dpres/"
            "file-scraper.git@develop#egg=file_scraper",
            "siptools@git+https://gitlab.ci.csc.fi/dpres/"
            "dpres-siptools.git@develop#egg=siptools"
        ],
        entry_points={
            "console_scripts": [
                "sip-compiler = dpres_sip_compiler.cmd:cli"
            ]
        },
    )


if __name__ == '__main__':
    main()
