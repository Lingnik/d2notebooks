
# Usage

See Setup/Installation section, later, for instructions on setting up Ted's Jupyter notebooks and the certs/secrets
needed for the API helper classes to also authenticate.

### ipython REPL with cached Destiny 2 manifests:

`fetch_components.py` is a helper script that downloads and caches the Destiny 2 manifests. The cache uses ~1.5GB of
RAM while running to make lookups fast. (This size can grow as the manifests mutate, a feature explained later.)

```python
$ ipython -i -c "exec(open('fetch_components.py').read())"
In [1]: 
```

The `api.manifest` object contains virtual references to each of Bungie's manifest collections, e.g.
`DestinyInventoryItemDefinition`, which itself is a (dynamically-created) class. You can get a list of cached
collections with `api.manifest.manifest_keys`, and there is magic that strips the `jsonWorldComponentContentPaths.` to
give you easy access to each collection. I'd like to add these to dir(api.manifest) at some point, but the hack works.

```python
In [1]: api.manifest.manifest_keys
Out [1]:
{'Manifest': '/Platform/Destiny2/Manifest/',
 'jsonWorldComponentContentPaths.DestinyNodeStepSummaryDefinition': '/common/destiny2_content/json/en/DestinyNodeStepSummaryDefinition-7ad64fed-df6a-4a3a-9579-3ab4e5a5b65b.json',
 'jsonWorldComponentContentPaths.DestinyArtDyeChannelDefinition': '/common/destiny2_content/json/en/DestinyArtDyeChannelDefinition-7ad64fed-df6a-4a3a-9579-3ab4e5a5b65b.json',
[...]
 'jsonWorldComponentContentPaths.DestinyFireteamFinderConstantsDefinition': '/common/destiny2_content/json/en/DestinyFireteamFinderConstantsDefinition-7ad64fed-df6a-4a3a-9579-3ab4e5a5b65b.json'}
}

In [2]: items = api.manifest.DestinyInventoryItemDefinition
```

## Working with Collections (`ManifestComponentCollection`)

Collections contain a `manifest` attribute that is the JSON representation of the collection. In this interface, the
cached JSON representations are **mutable**, and may have additional keys injected at runtime in order to dereference
foreign keys that point to other collection types. (The only example of this right now is calling `item.sockets`,
which will dereference and merge in the socket plugs for an item instance to give you a friendlier view of the plugs 
that can be inserted into, e.g., a weapon's barrels or shaders socket.)

Collections are strongly-typed, so they are aware of what kind of components they contain:
```python
In [3]: type(items)
Out [3]: src.bungie_manifest.jsonWorldComponentContentPaths.DestinyInventoryItemDefinitionCollection
```

Collection classes are all `ManifestComponentCollection` objects:
```python
In [4]: t.__bases__
Out[4]: (src.manifest.component_collections.ManifestComponentCollection,)
```

Eventually, ManifestComponentCollections will be a Python iterable, but for now you can access the collection's keys
and index them, returning an instance of the manifest's component class:
```python
In [5]: len(items.keys)
Out [5]: 26486
In [6]: items['1732779010']
Out [6]: <src.bungie_manifest.jsonWorldComponentContentPaths.DestinyInventoryItemDefinitionInstance at 0x708c6ab6be00>
```

### Collection Helpers

We have some helper methods for working with weapons.

#### Get all weapons (convenience helper vs find()):
```python
weapons = items.weapons()
```
**-or-**
```python
weapons = items.find(types='weapon')
```

#### Get a list of weapon traits:
```python
items.weapon_traits
```

#### Find a weapon by trait:
```python
items.weapons_with_trait('foundry.omolon')
```

#### Get a list of weapon types:
```python
items.weapon_types
```

#### Find a weapon:

ManifestComponentCollections have a `collection.find()` method that lets you search for items that match certain
conditions. The method signature is (at time of writing):

```python
def find(self, obj_name = None, types = None, trait = None, item_type = None, tier = None) -> list(ManifestComponent):
```

The resulting list contains objects that follow the ManifestComponent spec described later.

All of `find()`'s parameters are optional. (Yes, you can do a bare `collection.find()`.) The result is 
* `obj_name`: The friendly name of the object, e.g. `Scintillation`; searches `displayProperties.name`
* `types` (str or list): A type specific to this library, currently only `weapon`
  * Design note: This is because each weapon may appear in DestinyInventoryItemDefinition three times, but only
    one of them is the one you can have an instance of in your inventory. (The others are likely used to make
    them show up in vendor inventories, collections, etc.) So, we need to do a three-way filter in order to find
    only the instanceable weapons.
* `trait` (str): An item trait, e.g. `foundry.foo`, `faction.foo`, `activities.foo`, or `item.weapon.foo`; searches
  `traitIds`
  * Note: items can have multiple traits, and you may only search for one at a time
* `item_type` (str): The friendly item type name, e.g. 'Linear Fusion Rifle'; searches `itemTypeDisplayName`
* `tier` (str): The item's tier, e.g. `Common`, `Legendary`, `Exotic`; searches `.inventory.tierTypeName`

```python
sci = items.find('Scintillation', types='weapon')[0]
```

#### View frames for a set of weapons:

`collection.socket_category_defaults` takes a "socket category" and, optionally, any of the parameters accepted
by `collection.find()`. Some sockets have a "default", which is a useful shortcut to see the types of plugs it takes.
The category `intrinsics`, for example, maps to a weapon's "frame" (Adaptive, Aggressive, etc.), and the default is
the only entry in the plug set, so it ends up being a convenient proxy for "what frame is this?"

```python
In [2]: inv.socket_category_defaults('intrinsics', types='weapon', obj_name='Scintillation')
Out[2]: {'Adaptive Burst'}
```

You can also use it to obtain a list of frames for a collection of related weapons.

```python
leg = items.socket_category_defaults('intrinsics', types='weapon', tier='Legendary')
lfr = items.socket_category_defaults('intrinsics', types='weapon', item_type='Linear Fusion Rifle', tier='Legendary')
```

Note: This same method works for other socket types, too... such as barrels. Weapon perks are less-strongly-typed,
e.g. the left and right perks are of the same category. Confusingly, both left and right perks are referred to as
`frames` in the manifests, where we normally think of `intrinsics` as "frames"... welcome to the Bungie API. I will
probably refactor this call to return a list of lists in cases like this, or perhaps all cases regardless of if a
socket is duplicated or not.

```python
items.socket_category_defaults('frames', obj_name='Scintillation'), types='weapon')
```

## Working with Component Instances (`ManifestComponent`)

Instances of components are also dynamically-created classes who inherit from the base `ManifestComponent` class. Like
collections, they have some helper methods available. Note that instance can also refer to "an individual item owned by
your Guardian, which is not the meaning here, but rather, simply an instance of a component in a manifest collection.

```python
In [n]: sci = items.find('Scintillation', types='weapon')[0]
```

### View a weapon's manifest

The `manifest` property returns the JSON blob for the instance from the manifest.

**NOTE:** `manifest` is mutable and, like all objects in Python, pass-by-reference. Some methods, such as
`item.sockets`, will mutate the manifest by annotating the sockets and plugs with dereferenced instances of other
collection types based on foreign key/hash lookups from other collections. After `sockets` is called, those
dereferenced data are added to the cache. It's a cache, so we cache things in it as needed, because we're lazy, late
optimizers.

```python
In [n]: sci.manifest.get('displayProperties').get('name')
Out [n]: 'Scintillation'
```

### Collection Helpers

I added some helpers for some of the attributes in the manifest.

```python
In [n]: sci.properties.display_name
Out [n]: 'Scintillation'
```

#### View a weapon's frame:

```python
In [n]: sci.weapon_frame
Out [n]: 'Adaptive Burst'
```

Note: this leverages another helper method, `socket_default_for_category`, which you can call directly:

```python
s.socket_default_for_category('intrinsics')
```

This helper method looks up the `singleInitialItemName` from the socket. Note that this isn't useful if there are
multiple sockets with the same category, e.g. `frames`.

#### View a weapon's base stats:

Weapons have base stats that are further adjusted in-game when their sockets are plugged. For example, certain barrels
or perks will adjust the base stats up or down. This value is a useful metric of a weapon model's intrinsic potential
before taking its perks into account.

```python
sci.stats
```

#### View a weapon's breaker type:

Returns -- if it has one -- the item's intrinsic champion breaker type: Barrier, Unstoppable, or Overload. Note that
some weapons' `breaker_type` (such as The Lament) will be None, for example if their breaker comes from its masterwork.

```python
sci.breaker_type
```

#### View a weapon's sockets:

`sockets` is a property on items that fetches the sockets.socketEntries and hydrates each (in the mutable manifest
cache) from its socketTypeHash, socketType.socketCategoryHash, singleInitialItemhash, randomizedPlugSetHash, and
reusablePlugSetHash foreign keys to make working with sockets and plugs easier. As a result, anything that calls
`sockets` on a component instance will mutate the cache.

```python
sci.sockets
```

A sample (hydrated) socket:

```python
# These are the raw manifest attributes:
[{'socketTypeHash': 1215804696,
  'singleInitialItemHash': 831391274,
  'reusablePlugItems': [{'plugItemHash': 831391274}],
  'randomizedPlugSetHash': 3641544301,
...
# These are the hydrated additions:
   'socketCategory': {'displayProperties': {'description': 'Perks are built in to a given weapon. They can be swapped out an unlimited number of times.',
     'name': 'WEAPON PERKS',
     'hasIcon': False},
    'uiCategoryStyle': 2656457638,
    'categoryStyle': 1,
    'hash': 4241085061,
    'index': 18,
    'redacted': False,
    'blacklisted': False}},
  'singleInitialItemName': 'Hatchling',
  'randomizedPlugSet': {3708227201: {'name': 'Surrounded',
    'currentlyCanRoll': True},
   831391274: {'name': 'Hatchling', 'currentlyCanRoll': True},
   1427256713: {'name': 'Reservoir Burst', 'currentlyCanRoll': True},
   3078487919: {'name': 'Bait and Switch', 'currentlyCanRoll': True},
   1771339417: {'name': 'Firing Line', 'currentlyCanRoll': True},
   243981275: {'name': 'Attrition Orbs', 'currentlyCanRoll': True},
   781192741: {'name': 'Surrounded', 'currentlyCanRoll': False},
   102912326: {'name': 'Hatchling', 'currentlyCanRoll': False},
   254337357: {'name': 'Reservoir Burst', 'currentlyCanRoll': False},
   3744057135: {'name': 'Bait and Switch', 'currentlyCanRoll': False},
   395388285: {'name': 'Firing Line', 'currentlyCanRoll': False},
   984655331: {'name': 'Attrition Orbs', 'currentlyCanRoll': False}},
  'reusablePlugSet': {}}]
```

As you can see, the plug sets can include perks that can't currently roll, and in Scintillation's case (as an
enhanceable weapon, perhaps?) has duplicates of each plug.


# Setup/Installation

I'm using VSCode's python and jupyter plugins to run the notebook: 

* https://marketplace.visualstudio.com/items?itemName=ms-python.python
* https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter


## Install pyenv-virtualenv

I use [pyenv](https://github.com/pyenv/pyenv) and [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv) for managing python and installing virtual environments.  On the Mac, they can be installed with homebrew using:

```
brew update
brew install pyenv pyenv-virtualenv
```

and you can add this to your `.zshrc` to get it to automatically load the shims in your terminal with:

```
if command -v pyenv >/dev/null 2>&1; then
  export PYENV_ROOT="$HOME/.pyenv"
  export PATH="$PYENV_ROOT/bin:$PATH"
  eval "$(pyenv init -)"
  eval "$(pyenv virtualenv-init -)"
else
  echo "missing pyenv, install with:"
  echo "brew install pyenv"
  echo "pyenv install 3.12.2"
fi
```

## Create a Python Envirnoment and Install Dependencies

Then run `./mkenv.sh` from the command-line to install the version of Python
defined in .python-version, create the virtual environment named in that file,
and install the Python dependencies needed by this project using pip.

Alternatively, you'll learn a bit more about how pyenv works if you follow the
alternative instructions below:

### Alternative (manual) Instructions

Install python and create a new virtual environment for this notebook with:

```
pyenv install 3.12.2

# make it the global python if desired:
pyenv global 3.12.2

# create the virtual environment used in .python-version:
pyenv virtualenv 3.12.2 d2notebooks-3.12.2
```

Now, when you're in this directory in your shell, you should see this as the active virtualenv:

```
which python
/Users/<your user>/.pyenv/shims/python

python -V
Python 3.12.2

pyenv versions
  system
  3.12.2
  3.12.2/envs/d2notebooks-3.12.2
* d2notebooks-3.12.2 --> /Users/<your user>/.pyenv/versions/3.12.2/envs/d2notebooks-3.12.2 (set by /Users/<your user>/<path to>/d2notebooks/.python-version)
```

Python (pip) typically stores dependencies in `requirements.txt` (or other modern replacements), install them with:

```
pip install -r requirements.txt
```

## Choose the Python kernel in VSCode

When you run the first python cell, VSCode will prompt you for the kernel to use.  You should be able to pick the `d2notebooks-3.12.2` kernel.
