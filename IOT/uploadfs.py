Import("env")
env.AddCustomTarget("uploadfs", None, "pio run --target uploadfs", "Upload SPIFFS")