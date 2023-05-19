# This is the function for "1. Find images based on the tags"
# Use this for testing by changing dbRecords and tagBundles

def find_images_based_on_tags(dbRecords, tagBundles):
    result = []
    tags = {}
    
    for tagBundle in tagBundles:
        tags[tagBundle['tag']] = tagBundle['count'] if "count" in tagBundle else 1

    for dbRecord in dbRecords:
        image_tags = {}
        for object in dbRecord['objects']:
            if object['label'] in image_tags:
                image_tags[object['label']] += 1
            else:
                image_tags[object['label']] = 1
    
        if all(tag in image_tags.keys() for tag in tags.keys()):
            if all(image_tags[tag] >= tags[tag] for tag in tags.keys()):
                result.append(dbRecord["image"])

    return {"links": result}


if __name__ == "__main__":
    dbRecords = [
    {
        "id": "ae8311ba-25d0-5669-a892-45906810ee31",
        "image": "000000141459.jpg",
        "objects": [
            {
                "accuracy": 0.4763828217983246,
                "label": "car"
            },
            {
                "accuracy": 0.3466882109642029,
                "label": "car"
            }
        ]
    },
    {
        "id": "2b807291-9781-5b61-9fde-08d856a1da41",
        "image": "000000275236.jpg",
        "objects": [
            {
                "accuracy": 0.6120065450668335,
                "label": "person"
            },
            {
                "accuracy": 0.38231420516967773,
                "label": "skis"
            },
            {
                "accuracy": 0.3466882109642029,
                "label": "car"
            },
            {
                "accuracy": 0.3466882109642029,
                "label": "desk"
            }
        ]
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