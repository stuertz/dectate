from confidant.app import App
from confidant.config import Config, Action
from confidant.error import ConflictError

import pytest


def test_simple():
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

        def identifier(self, my):
            return self.message

        def perform(self, obj, my):
            my.add(self.message, obj)

    class MyApp(App):
        testing_config = config

    @MyApp.foo('hello')
    def f():
        pass

    config.commit()

    assert MyApp.configurations.my.l == [('hello', f)]


def test_conflict_same_directive():
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

        def identifier(self, my):
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


def test_app_inherit():
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

        def identifier(self, my):
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


def test_app_override():
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

        def identifier(self, my):
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


def test_different_group_no_conflict():
    config = Config()

    class Registry(object):
        def __init__(self):
            self.l = []

        def add(self, message, obj):
            self.l.append((message, obj))

    @App.directive('foo')
    class FooDirective(Action):
        configurations = {
            'foo': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, foo):
            return self.message

        def perform(self, obj, foo):
            foo.add(self.message, obj)

    @App.directive('bar')
    class BarDirective(Action):
        configurations = {
            'bar': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, bar):
            return self.message

        def perform(self, obj, bar):
            bar.add(self.message, obj)

    class MyApp(App):
        testing_config = config

    @MyApp.foo('hello')
    def f():
        pass

    @MyApp.bar('hello')
    def g():
        pass

    config.commit()

    assert MyApp.configurations.foo.l == [('hello', f)]
    assert MyApp.configurations.bar.l == [('hello', g)]


def test_same_group_conflict():
    config = Config()

    class Registry(object):
        def __init__(self):
            self.l = []

        def add(self, message, obj):
            self.l.append((message, obj))

    @App.directive('foo')
    class FooDirective(Action):
        configurations = {
            'foo': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, foo):
            return self.message

        def perform(self, obj, foo):
            foo.add(self.message, obj)

    @App.directive('bar')
    class BarDirective(Action):
        configurations = {
            'bar': Registry
        }

        def __init__(self, message):
            self.message = message

        # should now conflict
        def group_key(self):
            return FooDirective

        def identifier(self, bar):
            return self.message

        def perform(self, obj, bar):
            bar.add(self.message, obj)

    class MyApp(App):
        testing_config = config

    @MyApp.foo('hello')
    def f():
        pass

    @MyApp.bar('hello')
    def g():
        pass

    with pytest.raises(ConflictError):
        config.commit()


def test_depends():
    config = Config()

    class Registry(object):
        def __init__(self):
            self.l = []

        def add(self, message, obj):
            self.l.append((message, obj))

    @App.directive('foo')
    class FooDirective(Action):
        configurations = {
            'my': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, my):
            return self.message

        def perform(self, obj, my):
            my.add(self.message, obj)

    @App.directive('bar')
    class BarDirective(Action):
        depends = [FooDirective]

        configurations = {
            'my': Registry
        }

        def __init__(self, message):
            self.message = message

        def identifier(self, my):
            return self.message

        def perform(self, obj, my):
            my.add(self.message, obj)

    class MyApp(App):
        testing_config = config

    @MyApp.bar('a')
    def g():
        pass

    @MyApp.foo('b')
    def f():
        pass

    config.commit()

    # since bar depends on foo, it should be executed last
    assert MyApp.configurations.my.l == [('b', f), ('a', g)]
