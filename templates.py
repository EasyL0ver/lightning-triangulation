from Modules import filtering as pre
from Modules import linelement as bsp


def pre_processing_template():
    hpfilter = pre.HPFilter(0.02, 101, 'hamming')
    prfilter = pre.RegionBasedBandStop(0.02, 30, mode='iir')
    hpfilter.children().append(prfilter)
    pre_processing_template = bsp.ProcessorTemplateBlock(hpfilter)
    return pre_processing_template.get_instance()



