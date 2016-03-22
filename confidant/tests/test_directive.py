from confidant.app import App
from confidant.config import Config, Action
from confidant.error import ConflictError

import pytest


def test_directive_main():
    config = Config()

    class Registry(object):
        def __init__(self):
            self.l = []

        def add(self, message, obj):
            self.l.append((message, obj))

    @App.directive('foo')
    class MyDirective(Action):
        configurations = {
            'my': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, registry):
            return self.message

        def perform(self, obj, my):
            my.add(self.message, obj)

    class MyApp(App):
        testing_config = config

    @MyApp.foo('hello')
    def f():
        pass

    config.commit()

    MyApp.configurations.my.l == [('hello', f)]


def test_directive_conflict():
    config = Config()

    class Registry(object):
        def __init__(self):
            self.l = []

        def add(self, message, obj):
            self.l.append((message, obj))

    @App.directive('foo')
    class MyDirective(Action):
        configurations = {
            'my': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, registry):
            return self.message

        def perform(self, obj, my):
            my.add(self.message, obj)

    class MyApp(App):
        testing_config = config

    @MyApp.foo('hello')
    def f():
        pass

    @MyApp.foo('hello')
    def f2():
        pass

    with pytest.raises(ConflictError):
        config.commit()


def test_directive_inherit():
    config = Config()

    class Registry(object):
        pass

    @App.directive('foo')
    class MyDirective(Action):
        configurations = {
            'my': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, registry):
            return self.message

        def perform(self, obj, my):
            my.message = self.message
            my.obj = obj

    class MyApp(App):
        testing_config = config

    class SubApp(MyApp):
        testing_config = config

    @MyApp.foo('hello')
    def f():
        pass

    config.commit()

    assert MyApp.configurations.my.message == 'hello'
    assert MyApp.configurations.my.obj is f
    assert SubApp.configurations.my.message == 'hello'
    assert SubApp.configurations.my.obj is f


def test_directive_override():
    config = Config()

    class Registry(object):
        pass

    @App.directive('foo')
    class MyDirective(Action):
        configurations = {
            'my': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, registry):
            return self.message

        def perform(self, obj, my):
            my.message = self.message
            my.obj = obj

    class MyApp(App):
        testing_config = config

    class SubApp(MyApp):
        testing_config = config

    @MyApp.foo('hello')
    def f():
        pass

    @SubApp.foo('hello')
    def f2():
        pass

    config.commit()

    assert MyApp.configurations.my.message == 'hello'
    assert MyApp.configurations.my.obj is f
    assert SubApp.configurations.my.message == 'hello'
    assert SubApp.configurations.my.obj is f2