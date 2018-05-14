from modeldatabase.Binary_models.model_db import get_model_out_dict
from utils.modelutils.layers.kldivg.initializers import *
from utils.modelutils.layers.kldivg.regularizers import *
from utils.modelutils.layers.kldivg.distances import *
from utils.modelutils.layers.kldivg.optimizers import *
def kl_vgg_baseline(opts, input_shape, nb_classes, getstring_flag=False):
    model_string = 'klconvb|f:64,r:3,bias:1->lsoft' \
                   '->klconv|f:64,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:128,r:3,bias:1->lsoft' \
                   '->klconv|f:128,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f: 512,r:3,bias:1->lsoft' \
                   '->klconv|f: 512,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f: 512,r: 1,bias:1->lsoft' \
                   '->klconv|f:{},r:1,bias:0->lsoft' \
                   '->flattensh->fin'.format(nb_classes)
    use_link_func = False
    linker = linker_abs
    kl_init = Dirichlet_Init(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts'] = {}
    opts['optimizer_opts']['loss']['method'] = kl_loss_data_centric
    opts['model_opts']['kl_opts']['klb_initial'] = Dirichlet_Init_Bin(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['kl_initial'] = kl_init
    opts['model_opts']['kl_opts']['convbreg'] = None
    opts['model_opts']['kl_opts']['convreg'] =None# MixEntReg(1,kl_init)
    opts['model_opts']['kl_opts']['dist_measure'] = kl_both_centric
    opts['model_opts']['kl_opts']['use_link_func'] = use_link_func
    opts['model_opts']['kl_opts']['biasreg'] = None
    return get_model_out_dict(opts, model_string=model_string)
def kl_vgg_baseline_conc(opts, input_shape, nb_classes, getstring_flag=False):
    model_string = 'klconvbconc|f:64,r:3,bias:1->lsoft' \
                   '->klconvconc|f:64,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvconc|f:128,r:3,bias:1->lsoft' \
                   '->klconvconc|f:128,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvconc|f:256,r:3,bias:1->lsoft' \
                   '->klconvconc|f:256,r:3,bias:1->lsoft' \
                   '->klconvconc|f:256,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvconc|f:512,r:3,bias:1->lsoft' \
                   '->klconvconc|f:512,r:3,bias:1->lsoft' \
                   '->klconvconc|f:512,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvconc|f:512,r:3,bias:1->lsoft' \
                   '->klconvconc|f: 512,r:3,bias:1->lsoft' \
                   '->klconvconc|f: 512,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvconc|f: 512,r: 1,bias:1->lsoft' \
                   '->klconvconc|f:{},r:1->lsoft' \
                   '->flattensh->fin'.format(nb_classes)
    use_link_func = False
    linker = linker_abs
    opts['model_opts']['kl_opts'] = {}
    opts['optimizer_opts']['loss']['method'] = kl_loss_data_centric
    opts['model_opts']['kl_opts']['convbreg'] = None
    opts['model_opts']['kl_opts']['convreg'] = None
    opts['model_opts']['kl_opts']['klb_initial'] = Dirichlet_Init_Bin(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['kl_initial'] = Dirichlet_Init(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['dist_measure'] = kl_both_centric
    opts['model_opts']['kl_opts']['use_link_func'] = use_link_func
    opts['model_opts']['kl_opts']['biasreg'] = None
    return get_model_out_dict(opts, model_string=model_string)
def kl_vgg_baseline_nat(opts, input_shape, nb_classes, getstring_flag=False):
    model_string = 'klconvb|f:64,r:3,bias:1->lsoft' \
                   '->klconv|f:64,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:128,r:3,bias:1->lsoft' \
                   '->klconv|f:128,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f: 512,r:3,bias:1->lsoft' \
                   '->klconv|f: 512,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f: 512,r: 1,bias:1->lsoft' \
                   '->klconv|f:{},r:1->lsoft' \
                   '->flattensh->fin'.format(nb_classes)
    use_link_func = False
    linker = linker_abs
    opts['model_opts']['kl_opts'] = {}
    opts['optimizer_opts']['loss']['method'] = kl_loss_data_centric
    opts['model_opts']['kl_opts']['convbreg'] =None
    opts['model_opts']['kl_opts']['convreg'] = None
    opts['model_opts']['kl_opts']['klb_initial'] = AlphaInitBin(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['kl_initial'] = AlphaInit(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['bias_initial'] = AlphaInitBias(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['dist_measure'] = kl_both_centric
    opts['model_opts']['kl_opts']['use_link_func'] = use_link_func
    opts['model_opts']['kl_opts']['biasreg'] = None
    opts['optimizer_opts']['lr'] = 0.001  # .1
    opts['optimizer_opts']['optimizer'] = PolarSGD(polar_decay=1.0,
                                                   lr=opts['optimizer_opts']['lr'],
                                                   momentum=0.9,
                                                   decay=0.0,
                                                   nesterov=False)
    return get_model_out_dict(opts, model_string=model_string)
def kl_vgg_baseline_concnat(opts, input_shape, nb_classes, getstring_flag=False):
    model_string = 'klconvbnat|f:64,r:3,bias:0->lsoft' \
                   '->klconvnat|f:64,r:3,bias:0->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvnat|f:128,r:3,bias:0->lsoft' \
                   '->klconvnat|f:128,r:3,bias:0->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvnat|f:256,r:3,bias:0->lsoft' \
                   '->klconvnat|f:256,r:3,bias:0->lsoft' \
                   '->klconvnat|f:256,r:3,bias:0->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvnat|f:512,r:3,bias:0->lsoft' \
                   '->klconvnat|f:512,r:3,bias:0->lsoft' \
                   '->klconvnat|f:512,r:3,bias:0->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvnat|f:512,r:3,bias:0->lsoft' \
                   '->klconvnat|f: 512,r:3,bias:0->lsoft' \
                   '->klconvnat|f: 512,r:3,bias:0->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconvnat|f: 512,r: 1,bias:0->lsoft' \
                   '->klconvnat|f:{},r:1->lsoft' \
                   '->flattensh->fin'.format(nb_classes)
    use_link_func = False
    linker = linker_abs
    opts['model_opts']['kl_opts'] = {}
    opts['optimizer_opts']['loss']['method'] = kl_loss_data_centric
    opts['model_opts']['kl_opts']['convbreg'] = None
    opts['model_opts']['kl_opts']['convreg'] = None
    opts['model_opts']['kl_opts']['klb_initial'] = AlphaInitBin(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['kl_initial'] = AlphaInit(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['bias_initial'] = AlphaInitBias(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['dist_measure'] = kl_both_centric
    opts['model_opts']['kl_opts']['use_link_func'] = use_link_func
    opts['model_opts']['kl_opts']['biasreg'] = None
    return get_model_out_dict(opts, model_string=model_string)
def kl_vgg_baseline_nat_square(opts, input_shape, nb_classes, getstring_flag=False):
    model_string = 'klconvb|f:64,r:3,bias:1->lsoft' \
                   '->klconv|f:64,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:128,r:3,bias:1->lsoft' \
                   '->klconv|f:128,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klconv|f:256,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f:512,r:3,bias:1->lsoft' \
                   '->klconv|f: 512,r:3,bias:1->lsoft' \
                   '->klconv|f: 512,r:3,bias:1->lsoft' \
                   '->klavgpool|r:2,s:2' \
                   '->klconv|f: 512,r: 1,bias:1->lsoft' \
                   '->klconv|f:{},r:1->lsoft' \
                   '->flattensh->fin'.format(nb_classes)
    use_link_func = True
    linker = linker_square
    opts['model_opts']['kl_opts'] = {}
    opts['optimizer_opts']['loss']['method'] = kl_loss_data_centric
    opts['model_opts']['kl_opts']['convbreg'] = None
    opts['model_opts']['kl_opts']['convreg'] = None
    opts['model_opts']['kl_opts']['klb_initial'] = UnitSphereInitBin(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['kl_initial'] = UnitSphereInit(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['bias_initial'] = UnitSphereInitBias(use_link_func=use_link_func, linker=linker)
    opts['model_opts']['kl_opts']['dist_measure'] = kl_both_centric
    opts['model_opts']['kl_opts']['use_link_func'] = use_link_func
    opts['model_opts']['kl_opts']['biasreg'] = None
    opts['optimizer_opts']['momentum'] = 0.9
    opts['optimizer_opts']['lr'] = 0.001  # .1
    opts['optimizer_opts']['optimizer'] = PolarSGD(polar_decay=1,
                                                   lr=opts['optimizer_opts']['lr'],
                                                   momentum=0.0,
                                                   decay=0.0,
                                                   nesterov=False)
    return get_model_out_dict(opts, model_string=model_string)
