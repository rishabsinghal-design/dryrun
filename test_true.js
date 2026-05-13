const helloWorld = require('./true');

test('helloWorld returns "Hello, World!"', () => {
    expect(helloWorld()).toBe("Hello, World!");
});
