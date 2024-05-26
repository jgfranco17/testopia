def before_all(context):
    context.setup_complete = True


def after_all(context):
    if context.setup_complete:
        # Perform teardown activities here
        context.teardown_complete = True


def before_scenario(context, scenario):
    context.response = None
