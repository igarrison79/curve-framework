from shopsync import ShopSync

def test_sync_inventory_message():
    syncer = ShopSync(system_of_record="Amazon")
    assert syncer.sync_inventory() == "Syncing inventory using Amazon as system of record"
