from cx_Freeze import setup, Executable

build_exe_options = {"packages" : [], "include_files" : ['config.ini', 'readme.md']}
setup(
        name = "Infinite Campus Grade Scraper",
        version = "1.0",
        options = {'build_exe' : build_exe_options},
        executables = [Executable("scraper.py")]
)
