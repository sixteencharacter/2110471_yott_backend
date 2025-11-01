from glob import glob
import os
import sys
import json
sys.path.append(os.getcwd())
from config import BASE_STICKER_PATH

class StickerManager :

    instance_ = None

    def __new__(cls) :
        if cls.instance_ is None :
            cls.instance_ = super().__new__(cls)
        return cls.instance_
    
    def __init__(self,*args,**kwargs) :

        if not hasattr(self,'_initialized') :
            self._initialized = True
            self.available_manifest_file = glob("./public/assets/stickers/manifest/*.json")
            self.available_manifest_mapping = dict()
            for f in self.available_manifest_file :
                try :
                    with open(f,"r") as fp :
                        manifest_data = json.load(fp)
                        # manifest_data["pictures"] = [BASE_STICKER_PATH + x for x in manifest_data["pictures"]]
                        self.available_manifest_mapping[manifest_data["package"]] = manifest_data
                except :
                    pass

    def get_user_sticker_access(self,*args,**kwargs) :
        return list(self.available_manifest_mapping.values())
    
stickerManager = StickerManager()
    
    
