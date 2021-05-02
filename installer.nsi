Name "Worldbuilding"

outfile "Installer.exe"
InstallDir $PROGRAMFILES\Worldbuilding

BrandingText "Worldbuilding: An app for Worldbuilders"

PageEx license
	LicenseData LICENSE.txt
	LicenseForceSelection radiobuttons "I Agree" "I disagree"
PageExEnd

PageEx directory
	Caption "Worldbuilding: Install folder"
PageExEnd

PageEx instfiles
	Caption "Worldbuilding: Installing"
PageExEnd

Section "Worldbuilding"
	SetOutPath $INSTDIR
	WriteUninstaller Uninstall.exe
	SetAutoClose true

	File  LICENSE.txt
    File  python3.dll
    File  python38.dll
    File  Worldbuilding.exe

    SetOutPath $INSTDIR\data
    File  data\favicon.png
    File  data\savedata.json

    SetOutPath $INSTDIR\lib
    File  lib\library.zip
    File  lib\unicodedata.pyd
    File  lib\_bz2.pyd
    File  lib\_decimal.pyd
    File  lib\_hashlib.pyd
    File  lib\_lzma.pyd
    File  lib\_queue.pyd

    SetOutPath $INSTDIR\lib\collections
    File  lib\collections\abc.pyc
    File  lib\collections\__init__.pyc

    SetOutPath $INSTDIR\lib\distutils
    File  lib\distutils\README
    File  lib\distutils\version.pyc
    File  lib\distutils\__init__.pyc

    SetOutPath $INSTDIR\lib\distutils\command
    File  lib\distutils\command\command_template
    File  lib\distutils\command\wininst-10.0-amd64.exe
    File  lib\distutils\command\wininst-10.0.exe
    File  lib\distutils\command\wininst-14.0-amd64.exe
    File  lib\distutils\command\wininst-14.0.exe
    File  lib\distutils\command\wininst-6.0.exe
    File  lib\distutils\command\wininst-7.1.exe
    File  lib\distutils\command\wininst-8.0.exe
    File  lib\distutils\command\wininst-9.0-amd64.exe
    File  lib\distutils\command\wininst-9.0.exe

    SetOutPath $INSTDIR\lib\distutils\tests
    File  lib\distutils\tests\includetest.rst
    File  lib\distutils\tests\Setup.sample

    SetOutPath $INSTDIR\lib\email
    File  lib\email\architecture.rst
    File  lib\email\base64mime.pyc
    File  lib\email\charset.pyc
    File  lib\email\contentmanager.pyc
    File  lib\email\encoders.pyc
    File  lib\email\errors.pyc
    File  lib\email\feedparser.pyc
    File  lib\email\generator.pyc
    File  lib\email\header.pyc
    File  lib\email\headerregistry.pyc
    File  lib\email\iterators.pyc
    File  lib\email\message.pyc
    File  lib\email\parser.pyc
    File  lib\email\policy.pyc
    File  lib\email\quoprimime.pyc
    File  lib\email\utils.pyc
    File  lib\email\_encoded_words.pyc
    File  lib\email\_header_value_parser.pyc
    File  lib\email\_parseaddr.pyc
    File  lib\email\_policybase.pyc
    File  lib\email\__init__.pyc

    CreateDirectory $INSTDIR\lib\email\mime

    SetOutPath $INSTDIR\lib\encodings
    File  lib\encodings\aliases.pyc
    File  lib\encodings\ascii.pyc
    File  lib\encodings\base64_codec.pyc
    File  lib\encodings\big5.pyc
    File  lib\encodings\big5hkscs.pyc
    File  lib\encodings\bz2_codec.pyc
    File  lib\encodings\charmap.pyc
    File  lib\encodings\cp037.pyc
    File  lib\encodings\cp1006.pyc
    File  lib\encodings\cp1026.pyc
    File  lib\encodings\cp1125.pyc
    File  lib\encodings\cp1140.pyc
    File  lib\encodings\cp1250.pyc
    File  lib\encodings\cp1251.pyc
    File  lib\encodings\cp1252.pyc
    File  lib\encodings\cp1253.pyc
    File  lib\encodings\cp1254.pyc
    File  lib\encodings\cp1255.pyc
    File  lib\encodings\cp1256.pyc
    File  lib\encodings\cp1257.pyc
    File  lib\encodings\cp1258.pyc
    File  lib\encodings\cp273.pyc
    File  lib\encodings\cp424.pyc
    File  lib\encodings\cp437.pyc
    File  lib\encodings\cp500.pyc
    File  lib\encodings\cp720.pyc
    File  lib\encodings\cp737.pyc
    File  lib\encodings\cp775.pyc
    File  lib\encodings\cp850.pyc
    File  lib\encodings\cp852.pyc
    File  lib\encodings\cp855.pyc
    File  lib\encodings\cp856.pyc
    File  lib\encodings\cp857.pyc
    File  lib\encodings\cp858.pyc
    File  lib\encodings\cp860.pyc
    File  lib\encodings\cp861.pyc
    File  lib\encodings\cp862.pyc
    File  lib\encodings\cp863.pyc
    File  lib\encodings\cp864.pyc
    File  lib\encodings\cp865.pyc
    File  lib\encodings\cp866.pyc
    File  lib\encodings\cp869.pyc
    File  lib\encodings\cp874.pyc
    File  lib\encodings\cp875.pyc
    File  lib\encodings\cp932.pyc
    File  lib\encodings\cp949.pyc
    File  lib\encodings\cp950.pyc
    File  lib\encodings\euc_jisx0213.pyc
    File  lib\encodings\euc_jis_2004.pyc
    File  lib\encodings\euc_jp.pyc
    File  lib\encodings\euc_kr.pyc
    File  lib\encodings\gb18030.pyc
    File  lib\encodings\gb2312.pyc
    File  lib\encodings\gbk.pyc
    File  lib\encodings\hex_codec.pyc
    File  lib\encodings\hp_roman8.pyc
    File  lib\encodings\hz.pyc
    File  lib\encodings\idna.pyc
    File  lib\encodings\iso2022_jp.pyc
    File  lib\encodings\iso2022_jp_1.pyc
    File  lib\encodings\iso2022_jp_2.pyc
    File  lib\encodings\iso2022_jp_2004.pyc
    File  lib\encodings\iso2022_jp_3.pyc
    File  lib\encodings\iso2022_jp_ext.pyc
    File  lib\encodings\iso2022_kr.pyc
    File  lib\encodings\iso8859_1.pyc
    File  lib\encodings\iso8859_10.pyc
    File  lib\encodings\iso8859_11.pyc
    File  lib\encodings\iso8859_13.pyc
    File  lib\encodings\iso8859_14.pyc
    File  lib\encodings\iso8859_15.pyc
    File  lib\encodings\iso8859_16.pyc
    File  lib\encodings\iso8859_2.pyc
    File  lib\encodings\iso8859_3.pyc
    File  lib\encodings\iso8859_4.pyc
    File  lib\encodings\iso8859_5.pyc
    File  lib\encodings\iso8859_6.pyc
    File  lib\encodings\iso8859_7.pyc
    File  lib\encodings\iso8859_8.pyc
    File  lib\encodings\iso8859_9.pyc
    File  lib\encodings\johab.pyc
    File  lib\encodings\koi8_r.pyc
    File  lib\encodings\koi8_t.pyc
    File  lib\encodings\koi8_u.pyc
    File  lib\encodings\kz1048.pyc
    File  lib\encodings\latin_1.pyc
    File  lib\encodings\mac_arabic.pyc
    File  lib\encodings\mac_centeuro.pyc
    File  lib\encodings\mac_croatian.pyc
    File  lib\encodings\mac_cyrillic.pyc
    File  lib\encodings\mac_farsi.pyc
    File  lib\encodings\mac_greek.pyc
    File  lib\encodings\mac_iceland.pyc
    File  lib\encodings\mac_latin2.pyc
    File  lib\encodings\mac_roman.pyc
    File  lib\encodings\mac_romanian.pyc
    File  lib\encodings\mac_turkish.pyc
    File  lib\encodings\mbcs.pyc
    File  lib\encodings\oem.pyc
    File  lib\encodings\palmos.pyc
    File  lib\encodings\ptcp154.pyc
    File  lib\encodings\punycode.pyc
    File  lib\encodings\quopri_codec.pyc
    File  lib\encodings\raw_unicode_escape.pyc
    File  lib\encodings\rot_13.pyc
    File  lib\encodings\shift_jis.pyc
    File  lib\encodings\shift_jisx0213.pyc
    File  lib\encodings\shift_jis_2004.pyc
    File  lib\encodings\tis_620.pyc
    File  lib\encodings\undefined.pyc
    File  lib\encodings\unicode_escape.pyc
    File  lib\encodings\utf_16.pyc
    File  lib\encodings\utf_16_be.pyc
    File  lib\encodings\utf_16_le.pyc
    File  lib\encodings\utf_32.pyc
    File  lib\encodings\utf_32_be.pyc
    File  lib\encodings\utf_32_le.pyc
    File  lib\encodings\utf_7.pyc
    File  lib\encodings\utf_8.pyc
    File  lib\encodings\utf_8_sig.pyc
    File  lib\encodings\uu_codec.pyc
    File  lib\encodings\zlib_codec.pyc
    File  lib\encodings\__init__.pyc

    SetOutPath $INSTDIR\lib\engine
    File  lib\engine\material_densities.json
    File  lib\engine\molecular_weight.json
    File  lib\engine\recomendation.json
    File  lib\engine\recomendations.txt
    File  lib\engine\unit_definitions.txt
    File  lib\engine\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\backend
    File  lib\engine\backend\eventhandler.pyc
    File  lib\engine\backend\randomness.pyc
    File  lib\engine\backend\textrect.pyc
    File  lib\engine\backend\textrect_readme.txt
    File  lib\engine\backend\util.pyc
    File  lib\engine\backend\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\equations
    File  lib\engine\equations\binary.pyc
    File  lib\engine\equations\galaxy.pyc
    File  lib\engine\equations\general.pyc
    File  lib\engine\equations\lagrange.pyc
    File  lib\engine\equations\orbit.pyc
    File  lib\engine\equations\planet.pyc
    File  lib\engine\equations\planetary_system.pyc
    File  lib\engine\equations\satellite.pyc
    File  lib\engine\equations\star.pyc
    File  lib\engine\equations\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend
    File  lib\engine\frontend\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\globales
    File  lib\engine\frontend\globales\constantes.pyc
    File  lib\engine\frontend\globales\group.pyc
    File  lib\engine\frontend\globales\renderer.pyc
    File  lib\engine\frontend\globales\textrect.pyc
    File  lib\engine\frontend\globales\textrect_readme.txt
    File  lib\engine\frontend\globales\widgethandler.pyc
    File  lib\engine\frontend\globales\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\graphs
    File  lib\engine\frontend\graphs\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\graphs\atmograph
    File  lib\engine\frontend\graphs\atmograph\atmograph.pyc
    File  lib\engine\frontend\graphs\atmograph\atmograph04rev24.png
    File  lib\engine\frontend\graphs\atmograph\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\graphs\common
    File  lib\engine\frontend\graphs\common\interpolaters.pyc
    File  lib\engine\frontend\graphs\common\objects.pyc
    File  lib\engine\frontend\graphs\common\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\graphs\dwarfgraph
    File  lib\engine\frontend\graphs\dwarfgraph\dwarfgraph.png
    File  lib\engine\frontend\graphs\dwarfgraph\dwarfgraph.pyc
    File  lib\engine\frontend\graphs\dwarfgraph\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\graphs\gasgraph
    File  lib\engine\frontend\graphs\gasgraph\gasgraph.png
    File  lib\engine\frontend\graphs\gasgraph\gasgraph.pyc
    File  lib\engine\frontend\graphs\gasgraph\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\graphs\graph
    File  lib\engine\frontend\graphs\graph\graph.pyc
    File  lib\engine\frontend\graphs\graph\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\graphs\graph\data
    File  lib\engine\frontend\graphs\graph\data\compositions.json
    File  lib\engine\frontend\graphs\graph\data\graph.png
    File  lib\engine\frontend\graphs\graph\data\lineas.json
    File  lib\engine\frontend\graphs\graph\data\mask.png

    SetOutPath $INSTDIR\lib\engine\frontend\visualization
    File  lib\engine\frontend\visualization\topdown_animated.pyc
    File  lib\engine\frontend\visualization\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\widgets
    File  lib\engine\frontend\widgets\basewidget.pyc
    File  lib\engine\frontend\widgets\incremental_value.pyc
    File  lib\engine\frontend\widgets\message.pyc
    File  lib\engine\frontend\widgets\meta.pyc
    File  lib\engine\frontend\widgets\object_type.pyc
    File  lib\engine\frontend\widgets\sprite_star.pyc
    File  lib\engine\frontend\widgets\values.pyc
    File  lib\engine\frontend\widgets\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\widgets\panels
    File  lib\engine\frontend\widgets\panels\asteroid_panel.pyc
    File  lib\engine\frontend\widgets\panels\atmosphere_panel.pyc
    File  lib\engine\frontend\widgets\panels\base_panel.pyc
    File  lib\engine\frontend\widgets\panels\layout_panel.pyc
    File  lib\engine\frontend\widgets\panels\naming_panel.pyc
    File  lib\engine\frontend\widgets\panels\planetary_orbit_panel.pyc
    File  lib\engine\frontend\widgets\panels\planet_panel.pyc
    File  lib\engine\frontend\widgets\panels\satellite_panel.pyc
    File  lib\engine\frontend\widgets\panels\star_panel.pyc
    File  lib\engine\frontend\widgets\panels\star_system_panel.pyc
    File  lib\engine\frontend\widgets\panels\stellar_orbit_panel.pyc
    File  lib\engine\frontend\widgets\panels\__init__.pyc

    SetOutPath $INSTDIR\lib\engine\frontend\widgets\panels\common
    File  lib\engine\frontend\widgets\panels\common\listed_body.pyc
    File  lib\engine\frontend\widgets\panels\common\modify_area.pyc
    File  lib\engine\frontend\widgets\panels\common\orbit_areas.pyc
    File  lib\engine\frontend\widgets\panels\common\planet_area.pyc
    File  lib\engine\frontend\widgets\panels\common\planet_button.pyc
    File  lib\engine\frontend\widgets\panels\common\text_button.pyc
    File  lib\engine\frontend\widgets\panels\common\__init__.pyc

    SetOutPath $INSTDIR\lib\importlib
    File  lib\importlib\abc.pyc
    File  lib\importlib\machinery.pyc
    File  lib\importlib\metadata.pyc
    File  lib\importlib\resources.pyc
    File  lib\importlib\util.pyc
    File  lib\importlib\_bootstrap.pyc
    File  lib\importlib\_bootstrap_external.pyc
    File  lib\importlib\__init__.pyc

    SetOutPath $INSTDIR\lib\json
    File  lib\json\decoder.pyc
    File  lib\json\encoder.pyc
    File  lib\json\scanner.pyc
    File  lib\json\__init__.pyc

    SetOutPath $INSTDIR\lib\logging
    File  lib\logging\__init__.pyc

    SetOutPath $INSTDIR\lib\packaging
    File  lib\packaging\py.typed
    File  lib\packaging\version.pyc
    File  lib\packaging\_structures.pyc
    File  lib\packaging\_typing.pyc
    File  lib\packaging\__about__.pyc
    File  lib\packaging\__init__.pyc

    SetOutPath $INSTDIR\lib\pint
    File  lib\pint\babel_names.pyc
    File  lib\pint\compat.pyc
    File  lib\pint\constants_en.txt
    File  lib\pint\context.pyc
    File  lib\pint\converters.pyc
    File  lib\pint\default_en.txt
    File  lib\pint\definitions.pyc
    File  lib\pint\errors.pyc
    File  lib\pint\formatting.pyc
    File  lib\pint\matplotlib.pyc
    File  lib\pint\measurement.pyc
    File  lib\pint\numpy_func.pyc
    File  lib\pint\pint-convert
    File  lib\pint\pint_eval.pyc
    File  lib\pint\quantity.pyc
    File  lib\pint\registry.pyc
    File  lib\pint\registry_helpers.pyc
    File  lib\pint\systems.pyc
    File  lib\pint\unit.pyc
    File  lib\pint\util.pyc
    File  lib\pint\xtranslated.txt
    File  lib\pint\__init__.pyc

    SetOutPath $INSTDIR\lib\pint\testsuite
    File  lib\pint\testsuite\conftest.pyc
    File  lib\pint\testsuite\helpers.pyc
    File  lib\pint\testsuite\test_application_registry.pyc
    File  lib\pint\testsuite\test_babel.pyc
    File  lib\pint\testsuite\test_compat.pyc
    File  lib\pint\testsuite\test_compat_downcast.pyc
    File  lib\pint\testsuite\test_compat_upcast.pyc
    File  lib\pint\testsuite\test_contexts.pyc
    File  lib\pint\testsuite\test_converters.pyc
    File  lib\pint\testsuite\test_dask.pyc
    File  lib\pint\testsuite\test_definitions.pyc
    File  lib\pint\testsuite\test_errors.pyc
    File  lib\pint\testsuite\test_formatter.pyc
    File  lib\pint\testsuite\test_infer_base_unit.pyc
    File  lib\pint\testsuite\test_issues.pyc
    File  lib\pint\testsuite\test_log_units.pyc
    File  lib\pint\testsuite\test_matplotlib.pyc
    File  lib\pint\testsuite\test_measurement.pyc
    File  lib\pint\testsuite\test_non_int.pyc
    File  lib\pint\testsuite\test_numpy.pyc
    File  lib\pint\testsuite\test_numpy_func.pyc
    File  lib\pint\testsuite\test_pint_eval.pyc
    File  lib\pint\testsuite\test_pitheorem.pyc
    File  lib\pint\testsuite\test_quantity.pyc
    File  lib\pint\testsuite\test_systems.pyc
    File  lib\pint\testsuite\test_umath.pyc
    File  lib\pint\testsuite\test_unit.pyc
    File  lib\pint\testsuite\test_util.pyc
    File  lib\pint\testsuite\__init__.pyc

    SetOutPath $INSTDIR\lib\pint\testsuite\baseline
    File  lib\pint\testsuite\baseline\test_basic_plot.png
    File  lib\pint\testsuite\baseline\test_plot_with_set_units.png

    SetOutPath $INSTDIR\lib\pygame
    File  lib\pygame\base.cp38-win32.pyd
    File  lib\pygame\bufferproxy.cp38-win32.pyd
    File  lib\pygame\bufferproxy.pyi
    File  lib\pygame\camera.pyi
    File  lib\pygame\color.cp38-win32.pyd
    File  lib\pygame\color.pyi
    File  lib\pygame\colordict.pyc
    File  lib\pygame\compat.pyc
    File  lib\pygame\constants.cp38-win32.pyd
    File  lib\pygame\constants.pyi
    File  lib\pygame\cursors.pyc
    File  lib\pygame\cursors.pyi
    File  lib\pygame\display.cp38-win32.pyd
    File  lib\pygame\display.pyi
    File  lib\pygame\draw.cp38-win32.pyd
    File  lib\pygame\draw.pyi
    File  lib\pygame\draw_py.pyc
    File  lib\pygame\event.cp38-win32.pyd
    File  lib\pygame\event.pyi
    File  lib\pygame\fastevent.cp38-win32.pyd
    File  lib\pygame\fastevent.pyi
    File  lib\pygame\font.cp38-win32.pyd
    File  lib\pygame\font.pyi
    File  lib\pygame\freesansbold.ttf
    File  lib\pygame\freetype.pyc
    File  lib\pygame\freetype.pyi
    File  lib\pygame\ftfont.pyc
    File  lib\pygame\gfxdraw.cp38-win32.pyd
    File  lib\pygame\gfxdraw.pyi
    File  lib\pygame\image.cp38-win32.pyd
    File  lib\pygame\image.pyi
    File  lib\pygame\imageext.cp38-win32.pyd
    File  lib\pygame\joystick.cp38-win32.pyd
    File  lib\pygame\joystick.pyi
    File  lib\pygame\key.cp38-win32.pyd
    File  lib\pygame\key.pyi
    File  lib\pygame\libFLAC-8.dll
    File  lib\pygame\libfreetype-6.dll
    File  lib\pygame\libjpeg-9.dll
    File  lib\pygame\libmodplug-1.dll
    File  lib\pygame\libmpg123-0.dll
    File  lib\pygame\libogg-0.dll
    File  lib\pygame\libopus-0.dll
    File  lib\pygame\libopusfile-0.dll
    File  lib\pygame\libpng16-16.dll
    File  lib\pygame\libtiff-5.dll
    File  lib\pygame\libvorbis-0.dll
    File  lib\pygame\libvorbisfile-3.dll
    File  lib\pygame\libwebp-7.dll
    File  lib\pygame\locals.pyc
    File  lib\pygame\macosx.pyc
    File  lib\pygame\mask.cp38-win32.pyd
    File  lib\pygame\mask.pyi
    File  lib\pygame\math.cp38-win32.pyd
    File  lib\pygame\math.pyi
    File  lib\pygame\midi.pyi
    File  lib\pygame\mixer.cp38-win32.pyd
    File  lib\pygame\mixer.pyi
    File  lib\pygame\mixer_music.cp38-win32.pyd
    File  lib\pygame\mouse.cp38-win32.pyd
    File  lib\pygame\mouse.pyi
    File  lib\pygame\music.pyi
    File  lib\pygame\newbuffer.cp38-win32.pyd
    File  lib\pygame\pixelarray.cp38-win32.pyd
    File  lib\pygame\pixelarray.pyi
    File  lib\pygame\pixelcopy.cp38-win32.pyd
    File  lib\pygame\pixelcopy.pyi
    File  lib\pygame\pkgdata.pyc
    File  lib\pygame\portmidi.dll
    File  lib\pygame\py.typed
    File  lib\pygame\pygame.ico
    File  lib\pygame\pygame_icon.bmp
    File  lib\pygame\pygame_icon.icns
    File  lib\pygame\pygame_icon.svg
    File  lib\pygame\pygame_icon.tiff
    File  lib\pygame\pypm.cp38-win32.pyd
    File  lib\pygame\python38.dll
    File  lib\pygame\rect.cp38-win32.pyd
    File  lib\pygame\rect.pyi
    File  lib\pygame\rwobject.cp38-win32.pyd
    File  lib\pygame\scrap.cp38-win32.pyd
    File  lib\pygame\scrap.pyi
    File  lib\pygame\SDL2.dll
    File  lib\pygame\SDL2_image.dll
    File  lib\pygame\SDL2_mixer.dll
    File  lib\pygame\SDL2_ttf.dll
    File  lib\pygame\sndarray.pyi
    File  lib\pygame\sprite.pyc
    File  lib\pygame\sprite.pyi
    File  lib\pygame\surface.cp38-win32.pyd
    File  lib\pygame\surface.pyi
    File  lib\pygame\surfarray.pyi
    File  lib\pygame\surflock.cp38-win32.pyd
    File  lib\pygame\sysfont.pyc
    File  lib\pygame\time.cp38-win32.pyd
    File  lib\pygame\time.pyi
    File  lib\pygame\transform.cp38-win32.pyd
    File  lib\pygame\transform.pyi
    File  lib\pygame\version.pyc
    File  lib\pygame\version.pyi
    File  lib\pygame\zlib1.dll
    File  lib\pygame\_camera_opencv_highgui.pyc
    File  lib\pygame\_camera_vidcapture.pyc
    File  lib\pygame\_dummybackend.pyc
    File  lib\pygame\_freetype.cp38-win32.pyd
    File  lib\pygame\_numpysndarray.pyc
    File  lib\pygame\_numpysurfarray.pyc
    File  lib\pygame\_sprite.cp38-win32.pyd
    File  lib\pygame\__init__.pyc
    File  lib\pygame\__init__.pyi

    SetOutPath $INSTDIR\lib\pygame\docs
    File  lib\pygame\docs\logos.html
    File  lib\pygame\docs\pygame_logo.gif
    File  lib\pygame\docs\pygame_powered.gif
    File  lib\pygame\docs\pygame_small.gif
    File  lib\pygame\docs\pygame_tiny.gif
    File  lib\pygame\docs\__init__.pyc
    File  lib\pygame\docs\__main__.pyc

    SetOutPath $INSTDIR\lib\pygame\threads
    File  lib\pygame\threads\__init__.pyc

    SetOutPath $INSTDIR\lib\pygame\_sdl2
    File  lib\pygame\_sdl2\audio.cp38-win32.pyd
    File  lib\pygame\_sdl2\controller.cp38-win32.pyd
    File  lib\pygame\_sdl2\mixer.cp38-win32.pyd
    File  lib\pygame\_sdl2\python38.dll
    File  lib\pygame\_sdl2\sdl2.cp38-win32.pyd
    File  lib\pygame\_sdl2\touch.cp38-win32.pyd
    File  lib\pygame\_sdl2\touch.pyi
    File  lib\pygame\_sdl2\video.cp38-win32.pyd
    File  lib\pygame\_sdl2\__init__.pyc
    File  lib\pygame\_sdl2\__init__.pyi

    SetOutPath $INSTDIR\lib\pygame\__pyinstaller
    File  lib\pygame\__pyinstaller\hook-pygame.pyc
    File  lib\pygame\__pyinstaller\__init__.pyc

    SetOutPath $INSTDIR\lib\urllib
    File  lib\urllib\parse.pyc
    File  lib\urllib\__init__.pyc

SectionEnd

Section "Uninstall"
    SetAutoClose true
	Delete $INSTDIR\Uninst.exe ; delete self
	RMDir /r $INSTDIR
SectionEnd