from yaml import safe_load
import os.path as osp


class ApplicationConfig(dict):

    def load(self, path):
        if not path:
            return self

        if not osp.exists(path):
            print(f"Config path {path} does not exist")
            return self

        with open(path, "r") as fp:
            self.update(safe_load(fp))
        return self

    def get_nested(self, key, default=None):
        split_keys = key.split(_DELIMITER)
        r = self
        for k in split_keys:
            r = r.get(k, default)
            if not isinstance(r, dict):
                break
        return r


_DELIMITER = "."
app_config = ApplicationConfig()
