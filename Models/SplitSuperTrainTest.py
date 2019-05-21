import csv
import random
import os

source_path = "data/supersegment-data.csv"
training_path = "data/supersegment-training.csv"
test_path = "data/supersegment-test.csv"

training_part = 0.7
random.seed(20180901)

writer_by_trip_id = {}
writer = None
current_trip_id = None

with open(source_path, newline="") as source_file, \
     open(training_path, "w", newline="") as training_file, \
     open(test_path, "w", newline="") as test_file:

    source_reader = csv.DictReader(source_file)
    training_writer = csv.DictWriter(training_file, source_reader.fieldnames)
    test_writer = csv.DictWriter(test_file, source_reader.fieldnames)

    training_writer.writeheader()
    test_writer.writeheader()

    for row in source_reader:
        if not row["trip_id"]:
            print(row)
            continue

        trip_id = int(row["trip_id"])

        if trip_id != current_trip_id:
            if trip_id not in writer_by_trip_id:
                if random.random() < training_part:
                    writer_by_trip_id[trip_id] = training_writer
                else:
                    writer_by_trip_id[trip_id] = test_writer

            current_trip_id = trip_id
            writer = writer_by_trip_id[trip_id]

        writer.writerow(row)
