import argparse
import logging
import pathlib

from .BusinessCardPipeline import BusinessCardPipeline


def main():
    parser = argparse.ArgumentParser(description='Perform NER on Business Cards. Please supply file')

    parser.add_argument('--file', required=True, help='File in "generated-business-cards" to be processed. If "all" is supplied, every file in "generated-business-cards" will be processed')
    parser.add_argument('--log_level', required=False, help='logging level used')
    
    args, unknown_args = parser.parse_known_args()

    log_level = args.log_level if args.log_level else "INFO" 
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("Business Card Processor")

    bcp = BusinessCardPipeline()
    if args.file == "all":
        for file in pathlib.Path("generated-business-cards").rglob("*"):
            if file.is_file():
                logging.info("Processing %s...", file)
                bcp.run(file_path=file)
                logging.info("completed %s!", file)
    else:
        logging.info("Processing %s", args.file)
        file_path = pathlib.Path("generated-business-cards") / args.file
        bcp.run(file_path=file_path)
        logging.info("completed %s!", args.file)


if __name__ == "__main__":
    main()
    