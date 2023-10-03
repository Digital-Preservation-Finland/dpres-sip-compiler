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
            "click"
        ],
        entry_points={
            "console_scripts": [
                "sip-compiler = dpres_sip_compiler.cmd:cli"
            ]
        },
    )


if __name__ == '__main__':
    main()
