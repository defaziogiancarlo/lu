# config values to add
hostname: currently hardcoded to vmlustre

# move stuff into lutils

# lutils needs to acess cfg.env as well, so lutils imports cfg, so cfg should not import lutils,
# cfg should import only from standard library