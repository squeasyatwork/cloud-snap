# This is the function for "3. Manual addition or removal of tags"
# Use this for testing by changing dbRecords and requestBody

def modify_image_tags(dbRecords, requestBody):
    tagBundles = requestBody["tags"]
    tags = {}
    for tagBundle in tagBundles:
        tags[tagBundle['tag']] = tagBundle['count'] if "count" in tagBundle else 1

    record_to_modify = {}
    for dbRecord in dbRecords:
        if dbRecord["image_url"] == requestBody["url"]:
            record_to_modify = dbRecord

    mode = requestBody["type"]

    if mode == 0:
        for tag in tags.keys():
            if tag in record_to_modify["objects"]:
                record_to_modify["objects"][tag] = max(record_to_modify["objects"][tag] - tags[tag], 0)
                if record_to_modify["objects"][tag] == 0:
                    record_to_modify["objects"].pop(tag)
    
    elif mode == 1:
        for tag in tags.keys():
            if tag in record_to_modify["objects"]:
                record_to_modify["objects"][tag] += tags[tag]
            else:
                record_to_modify["objects"][tag] = tags[tag]
    


if __name__ == "__main__":
    dbRecords = [
    {
        "id": "ae8311ba-25d0-5669-a892-45906810ee31",
        "image_url": "000000141459.jpg",
        "objects": {"car": 2}
    },
    {
        "id": "2b807291-9781-5b61-9fde-08d856a1da41",
        "image_url": "000000275236.jpg",
        "objects": {"person": 1, "skis": 1, "car": 1, "desk": 1}
    }
]

requestBody = {
    "url":"000000275236.jpg",
    "type": 1, # 1 for add and 0 for remove
    "tags": [
        {
            "tag": "person",
            "count": 2
        },
        {
            "tag": "alex",
            "count": 1
        }
    ]
}

modify_image_tags(dbRecords, requestBody)  

print(dbRecords)


requestBody = {
    "url":"000000275236.jpg",
    "type": 0, # 1 for add and 0 for remove
    "tags": [
        {
            "tag": "person",
            "count": 2
        },
        {
            "tag": "alex",
            "count": 1
        }
    ]
}

modify_image_tags(dbRecords, requestBody)  

print(dbRecords)

