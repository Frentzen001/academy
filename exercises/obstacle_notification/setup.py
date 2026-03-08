from setuptools import setup

package_name = 'obstacle_notification'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros',
    maintainer_email='ros@example.com',
    description='Obstacle notification system for linorobot2',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'obstacle_publisher = obstacle_notification.obstacle_publisher:main',
            'obstacle_subscriber = obstacle_notification.obstacle_subscriber:main',
        ],
    },
)
