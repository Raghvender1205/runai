import keras.optimizers

from runai import log
import runai.flex
import runai.ga

def compile(self, *args, **kwargs):
    if 'optimizer' in kwargs:
        assert len(args) == 0
        optimizer = kwargs['optimizer']
    else:
        assert len(args) == 1
        optimizer = args[0]

    # TODO(levosos): support cases when 'optimizer' is not an class instance but is either a string or a dictionary
    if not isinstance(optimizer, keras.optimizers.Optimizer):
        raise ValueError("'optimizer' must be a valid keras.optimizers.Optimizer")

    log.debug('compile() called with optimizer %s', optimizer)
    
    if runai.flex.gpus > 1:
        log.debug('Wrapping optimizer with Horovod')
        
        import horovod.keras as hvd
        optimizer = hvd.DistributedOptimizer(optimizer)

    if runai.flex.steps > 1:
        optimizer = runai.ga.keras.optimizers.Optimizer(optimizer, runai.flex.steps)

    kwargs['optimizer'] = optimizer

    return self.__runai__['compile'](**kwargs) # ignore 'args' as 'optimizer' is the only possible argument and it is in 'kwargs'

def fit(self, *args, **kwargs):
    log.debug('fit() called')

    if runai.flex.gpus > 1:
        import horovod.keras as hvd
        callbacks = [hvd.callbacks.BroadcastGlobalVariablesCallback(0)]

        if 'callbacks' in kwargs:
            callbacks.extend(kwargs['callbacks'])

        kwargs['callbacks'] = callbacks

    return self.__runai__['fit'](*args, **kwargs)

def fit_generator(self, *args, **kwargs):
    log.debug('fit_generator() called')

    if runai.flex.gpus > 1:
        import horovod.keras as hvd
        callbacks = [hvd.callbacks.BroadcastGlobalVariablesCallback(0)]

        if 'callbacks' in kwargs:
            callbacks.extend(kwargs['callbacks'])

        kwargs['callbacks'] = callbacks

    return self.__runai__['fit_generator'](*args, **kwargs)

def Model(model):
    __runai__ = {}

    for method in [compile, fit, fit_generator]: # TODO(levosos): what about evaluate() and predict()?
        __runai__[method.__name__] = getattr(model, method.__name__)
        setattr(model, method.__name__, method.__get__(model))
    
    setattr(model, '__runai__', __runai__)
    
    return model
