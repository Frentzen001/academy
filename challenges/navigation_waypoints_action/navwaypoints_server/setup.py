from setuptools import find_packages, setup

package_name = 'navwaypoints_server'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='humjie',
    maintainer_email='mingjiehu5@gmail.com',
    description='Testing server for navwaypoints_client',
    license='Apache License, Version 2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'navwaypoints_server = navwaypoints_server.navwaypoints_server:main',
        ],
    },
)
