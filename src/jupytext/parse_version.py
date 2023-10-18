def parse_version(version, custom_error=ImportError):
    try:
        from pkg_resources import parse_version as parse
    except ImportError:
        try:
            from packaging.version import parse
        except ImportError:
            raise custom_error("Please install either pkg_resources or packaging")

    print(version)
    return parse(version)
