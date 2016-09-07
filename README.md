# wallabag-migration

This python3 script takes a CSV file (formatted like the `testdata.csv` file) and the credentials from the `credentials.ini` to query the wallabag v2 API with it.

It is meant as an alternative way to migrate from wallabag v1 to v2 when the amount of articles is too big and the v1 export functionality only delivers 0-byte-sized JSON files. To get the CSV data you can export a CSV file from your wallabag v1 database with the help of [Adminer](https://www.adminer.org/) and the SQL command
```sql
SELECT `url`, `is_read`, `is_fav`
FROM `entries`
WHERE `user_id` = 'N';  # replace N by your actual user ID
```
After that you might need to convert the exported file from DOS to unix format with a command like
```bash
dos2unix sql.csv
```
and move it into the directory where the `post-articles.py` lies.

To start the actual migration copy the `credentials.ini.txt` and fill out the `credentials.ini` like
```bash
cp credentials.ini.txt credentials.ini
```

```ini
[DEFAULT]
host      = https://wallabag.example.org
username  = johndoe
password  = s3cr3tp4ssw0rd
client_id = 1_yaifiil7ooyaezohne9nei4azoopieshoo8eicae0moh2eumi
c_secret  = iquohme5naehee7ieg6ohsh0uo3aghaik3kiephi9jequoodoc
```
(you can get the client ID and secret by clicking on "developer" in your wallabag v2 and "create a new client" there) and execute
```bash
./post-articles.py sql.csv  # replace sql.csv by the actual CSV file name
```
This process might last quite a long time when you many articles so I'd recommend running it in a terminal multiplexer. In my case it ended with
```
posted 1304 articles
finished successfully.
./post-articles.py wallabag.csv  55,81s user 3,38s system 0% cpu 2:19:34,25 total
```
