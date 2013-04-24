from cx_Freeze import setup, Executable

includes = ['encodings.latin_1', 'encodings.utf_8', 'encodings.idna', 'encodings.ascii']
setup(
        name = "Infinite Campus Grade Scraper",
        version = "1.0",
        author = "Ben doan",
        options = {'build_exe' : {'includes' : includes}},
        executables = [Executable("scraper.py")]
)
