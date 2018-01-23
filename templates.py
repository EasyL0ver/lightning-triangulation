from Modules import filtering as pre
from Modules import linelement as bsp


def pre_processing_template():
    hpfilter = pre.HPFilter(0.05, 101, 'hamming')
    prfilter = pre.RegionBasedBandStop(0.02, 101)
    hpfilter.children().append(prfilter)
    pre_processing_template = bsp.ProcessorTemplateBlock(hpfilter)
    return pre_processing_template.get_instance()



