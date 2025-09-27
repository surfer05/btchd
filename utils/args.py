import argparse

class Args(argparse.Namespace):
    def __getattr__(self, name):
        # Return None if the attribute doesn't exist
        return None