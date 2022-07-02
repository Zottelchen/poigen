# POIGen

This is a temporary workaround for Minecraft Overviewer. Since 1.17 Minecraft moved some entities from the chunks to an extra folder in the world called 'entities'. Since Overviewer is not updated to deal with this yet, this little tool was written. 

## Usage
### Windows Build

### From Source
1. Clone repository
2. Install requirements: `pip install -r requirements.txt`
3. Run `python poigen.py --help` to see all options

## Limitations

* It is intended for the use of the map.drehmal.cyou - you might not need all the features that map offers.
* This only works with the overworld and currently the render has to be named "normalrender".
* It will overwrite whatever is in its way.
* Make sure to back up your world. It shouldn't write anything there. But how much can you trust a single tired IT guy really?
* It only does what it was programmed to do. There are no config options.
* It does not handle players at all.
* Exports are currently hardcoded.
* In comparison to the old config, this script assumes that Enchanted Books do have Enchantments on them. God be with you, if that isn't the case.
* It is single threaded and might be slower than Overviewer.
* Please use Overviewer --genpoi once it is patched.
* This does not contain Minecraft assets needed for icons and images. Get them from somewhere else.