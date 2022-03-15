"""Install SIP Compiler."""
from setuptools import setup


def main():
    """Install SIP Compiler."""
    setup(
        name='dpres-sip-compiler',
        packages=['dpres_sip_compiler'],
        package_dir={
            "dpres_sip_compiler": "dpres_sip_compiler"
        },
        include_package_data=True,
        install_requires=[
            "click",
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
