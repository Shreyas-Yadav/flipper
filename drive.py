import logging

log = logging.getLogger(__name__)


def append_to_doc(text: str, page_num: int) -> None:
    # TODO: implement Google Drive OAuth + Docs API upload
    log.info("Drive stub — page %d, %d chars (upload not yet implemented)", page_num, len(text))
