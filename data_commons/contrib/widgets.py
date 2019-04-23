def AddAttrs(additional_attrs):
    '''
    Quick & Dirty Mixin Factory for installing attributes on your custom widgets
    '''
    class AddAttrsMixin:
        def build_attrs(self, *args, **kwargs):
            attrs = super(AddAttrsMixin, self).build_attrs(*args, **kwargs)
            attrs.update(additional_attrs)
            return attrs
    return AddAttrsMixin
