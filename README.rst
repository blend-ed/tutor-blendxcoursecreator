blendxcoursecreator plugin for `Tutor <https://docs.tutor.edly.io>`__
#####################################################################

This plugin integrates the Blend-ed AI Course Creator API into your Open edX platform. It deploys a FastAPI application that provides AI-powered course creation capabilities with multi-tenant support.

The plugin includes:
- **BlendxCCApp FastAPI**: REST API for course creation and management
- **Celery Workers**: Background task processing for course generation
- **MySQL Database**: Data storage for courses and users
- **Redis Integration**: Message broker for Celery tasks

Installation
************

.. code-block:: bash

    pip install git+https://github.com/blend-ed/tutor-blendxcoursecreator

Usage
*****

Enable the plugin
=================

.. code-block:: bash

    tutor plugins enable blendxcoursecreator

Configuration
=============

Set required API keys and configuration:

.. code-block:: bash

    # Portkey API key for AI services
    tutor config save --set BLENDXCOURSECREATOR_PORTKEY_API_KEY=your-portkey-key

    # Admin secret key for organization management
    tutor config save --set BLENDXCCAPP_ADMIN_SECRET_KEY=your-admin-key

Build the Docker image
======================

.. code-block:: bash

    tutor images build blendxccapp

Launch the platform
===================

.. code-block:: bash

    tutor local launch

API Access
==========

The BlendxCCApp API will be available at:

- **Production**: ``http://aicc.{{ LMS_HOST }}``
- **Development**: ``http://aicc.{{ LMS_HOST }}:8010``

API Endpoints
=============

Admin Routes (X-Admin-Key header required)
-------------------------------------------

- ``POST /admin/orgs`` - Create organization
- ``GET /admin/orgs`` - List organizations
- ``GET /admin/orgs/{id}/reveal-key`` - View API key
- ``POST /admin/orgs/{id}/extend`` - Extend expiry

Client Routes (X-API-Key header required)
-----------------------------------------

- ``POST /api/v1/courses/create`` - Create course
- ``GET /api/v1/courses`` - List courses
- ``GET /api/v1/courses/{id}`` - Get course details
- ``GET /api/v1/courses/{id}/download`` - Download course
- ``POST /api/v1/courses/{id}/retry`` - Retry failed course
- ``DELETE /api/v1/courses/{id}`` - Delete course

Health Check
============

.. code-block:: bash

    # Check API health
    curl http://aicc.{{ LMS_HOST }}/health

    # Check database connectivity
    curl http://aicc.{{ LMS_HOST }}/health/db

First Time Setup
================

1. Create your first organization:

.. code-block:: bash

    curl -X POST http://aicc.{{ LMS_HOST }}/admin/orgs \
      -H "X-Admin-Key: your-admin-secret-key" \
      -H "Content-Type: application/json" \
      -d '{"name": "Your Organization", "contact_email": "admin@yourorg.com", "expiry_days": 365}'

2. Save the returned ``api_key`` for client API calls.

Services
========

The plugin deploys these services:

- **blendxccapp**: FastAPI application server
- **blendxccapp-celery**: Celery worker for background tasks
- **blendxccapp-job**: Initialization job

Development
===========

For development with hot-reload:

.. code-block:: bash

    # Enable development mode
    tutor config save --set DEBUG=true

    # Launch in development mode
    tutor local launch

The API will be available at ``http://aicc.{{ LMS_HOST }}:8010`` with hot-reload enabled.

Database
========

The plugin uses MySQL for data storage. The database ``blendxccapp`` is automatically created during initialization.

Webhook Notifications
====================

Configure webhook notifications for course completion:

.. code-block:: bash

    curl -X PUT http://aicc.{{ LMS_HOST }}/api/v1/webhooks/configure \
      -H "X-API-Key: your-org-api-key" \
      -H "Content-Type: application/json" \
      -d '{"webhook_url": "https://your-webhook-url.com/callback"}'

Required Configuration
=======================

Minimum required settings:

.. code-block:: bash

    BLENDXCOURSECREATOR_PORTKEY_API_KEY=your-portkey-key
    BLENDXCCAPP_ADMIN_SECRET_KEY=your-admin-key

Optional settings:

.. code-block:: bash

    # Synthesia API (for video generation)
    SYNTHESIA_API_KEY=your-synthesia-key
    SYNTHESIA_TEMPLATE_ID=your-template-id
    SYNTHESIA_AVATAR_ID=your-avatar-id

    # Tavily API (for video search)
    TAVILY_API_KEY=your-tavily-key

License
*******

This software is licensed under the terms of the AGPLv3.
