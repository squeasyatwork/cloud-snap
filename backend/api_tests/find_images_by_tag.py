# This is the function for "1. Find images based on the tags"
# Use this for testing by changing dbRecords and tagBundles

def find_images_based_on_tags(dbRecords, tagBundles):
    result = []
    tags = {}
    
    # Change how tags are structured from [{"tag": "sample1", "count": 1},{"tag": "sample2", "count": 2}] to {sample1: 1, sample2: 2}
    for tagBundle in tagBundles:
        tags[tagBundle['tag']] = tagBundle['count'] if "count" in tagBundle else 1

    # Iterate through records in the database and find records which are a superset of the input and have a count >= to each tag in the input 
    for dbRecord in dbRecords:
        if all(tag in dbRecord["objects"].keys() for tag in tags.keys()):
            if all(dbRecord["objects"][tag] >= tags[tag] for tag in tags.keys()):
                result.append(dbRecord["image_url"])

    return {"links": result}


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

    tagBundles = [
    {
        "tag": "person",
        "count": 1
    },
    {
        "tag": "desk",
        "count": 1
    },
    {
        "tag": "car"
    }
]

    print(find_images_based_on_tags(dbRecords, tagBundles))    